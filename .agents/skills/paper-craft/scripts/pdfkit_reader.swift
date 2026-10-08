import AppKit
import PDFKit
import Foundation

// Read supplied PDFs only; this helper never compiles TeX or writes PDF documents.
let args = CommandLine.arguments
func fail(_ message: String) -> Never {
    FileHandle.standardError.write(Data((message + "\n").utf8))
    exit(1)
}
guard args.count >= 3, let document = PDFDocument(url: URL(fileURLWithPath: args[2])),
      !document.isLocked else { fail("Cannot open PDF, or password required") }
if args[1] == "inspect" {
    var metadata: [String: String] = [:]
    for (key, value) in document.documentAttributes ?? [:] {
        metadata[String(describing: key)] = String(describing: value)
    }
    let pages = (0..<document.pageCount).map { document.page(at: $0)?.string ?? "" }
    let result: [String: Any] = ["page_count": document.pageCount, "metadata": metadata, "pages": pages]
    do {
        let data = try JSONSerialization.data(withJSONObject: result, options: [.sortedKeys])
        FileHandle.standardOutput.write(data)
    } catch { fail(error.localizedDescription) }
} else if args[1] == "render" {
    guard args.count == 6, let number = Int(args[3]), number > 0,
          let page = document.page(at: number - 1), let dpi = Double(args[5]),
          dpi >= 36, dpi <= 300 else { fail("Invalid page or DPI") }
    let bounds = page.bounds(for: .mediaBox)
    let size = NSSize(width: bounds.width * dpi / 72, height: bounds.height * dpi / 72)
    guard size.width > 0, size.height > 0, size.width * size.height <= 40_000_000 else {
        fail("Page exceeds render size limit")
    }
    let image = page.thumbnail(of: size, for: .mediaBox)
    guard let tiff = image.tiffRepresentation, let bitmap = NSBitmapImageRep(data: tiff),
          let png = bitmap.representation(using: .png, properties: [:]) else { fail("PNG render failed") }
    do { try png.write(to: URL(fileURLWithPath: args[4]), options: .withoutOverwriting) }
    catch { fail(error.localizedDescription) }
} else { fail("Unknown operation") }
