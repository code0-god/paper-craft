# Paper Craft

Computer Architecture / Computer Systems 연구자를 위한 논문 작성·검토 Agent Skill입니다. 연구 질문과 기여를 정리하고, 논증과 실험 근거를 검토하며, 저자의 기술적 의미를 보존하는 퇴고를 지원합니다.

Codex에서 `$paper-craft`로 호출합니다. Skill 본체는 [`.agents/skills/paper-craft/`](.agents/skills/paper-craft/SKILL.md)에 있으며, 디렉터리 전체를 독립적으로 설치할 수 있습니다.

## 빠른 시작

**필요 환경:** Agent Skills를 지원하는 Codex 또는 호환 호스트, Python 3.10+. npm/npx 설치에는 Node.js 18.3+가 필요합니다.

현재 npm 릴리스는 준비 중입니다. GitHub 소스로 설치하려면:

```bash
git clone https://github.com/code0-god/paper-craft.git
cd paper-craft
npm pack
npm install --global ./code0-god-paper-craft-0.1.0.tgz
paper-craft install
```

위 파일명은 0.1.0 기준입니다. 다른 버전에서는 `npm pack`이 출력한 파일명을 사용합니다. 설치 대상은 기본적으로 `~/.agents/skills/paper-craft`입니다. npm 패키지 설치 후 `paper-craft install`을 실행해야 호스트가 사용할 Skill이 복사됩니다.

연구 저장소에서 Codex를 실행하고 다음과 같이 요청합니다. 스킬이 보이지 않으면 세션을 다시 시작합니다.

```text
$paper-craft main.tex의 연구 기여와 실험 근거를 검토해줘.
```

## 설치 방법

### npm 릴리스 사용

레지스트리에 릴리스가 게시된 뒤에는 npx로 바로 설치할 수 있습니다.

```bash
npx --yes @code0-god/paper-craft@latest install
```

전역 CLI를 유지하려면:

```bash
npm install --global @code0-god/paper-craft@latest
paper-craft install
```

### 프로젝트 또는 지정 경로에 설치

전역 CLI를 설치한 뒤, 대상 연구 저장소에서 실행합니다.

```bash
paper-craft install --project
paper-craft install --destination "/path/to/research/.agents/skills/paper-craft"
```

| 옵션 | 설치 위치 |
| --- | --- |
| `--user` 또는 옵션 생략 | `~/.agents/skills/paper-craft` |
| `--project` | 현재 작업 디렉터리의 `.agents/skills/paper-craft` |
| `--destination PATH` | 지정한 전체 디렉터리; 마지막 이름은 `paper-craft` |

세 대상 옵션은 함께 사용할 수 없습니다. Python 실행 파일은 `--python /path/to/python3` 또는 `PAPER_CRAFT_PYTHON` 환경변수로 지정합니다. 사용 가능한 명령은 `paper-craft --help`, CLI 버전은 `paper-craft --version`으로 확인합니다.

### npm 없이 설치

이 저장소에서는 프로젝트 로컬 Skill을 바로 사용할 수 있습니다. 다른 프로젝트나 사용자 경로로 복사하려면 저장소 루트에서 실행합니다.

```bash
python3 .agents/skills/paper-craft/scripts/install_skill.py \
  --destination "$HOME/.agents/skills/paper-craft"
```

수동 설치는 대상 디렉터리가 없을 때 Skill 전체를 복사합니다.

```bash
mkdir -p "$HOME/.agents/skills"
cp -R .agents/skills/paper-craft "$HOME/.agents/skills/paper-craft"
```

Codex의 Skill Installer로도 설치할 수 있습니다.

```text
$skill-installer https://github.com/code0-god/paper-craft/tree/main/.agents/skills/paper-craft
사용자 경로 ~/.agents/skills에 설치해줘.
```

설치 위치와 발견 방식은 [Codex 공식 Skill 문서](https://learn.chatgpt.com/docs/build-skills)를 참고하세요.

## 업데이트

npm 릴리스에서 설치했다면:

```bash
npx --yes @code0-god/paper-craft@latest update
# 프로젝트 로컬 설치
npx --yes @code0-god/paper-craft@latest update --project
```

전역 CLI를 사용하는 경우 npm 패키지를 먼저 갱신하고 Skill에 반영합니다.

```bash
npm install --global @code0-god/paper-craft@latest
paper-craft update
```

GitHub 소스에서 설치했다면 해당 checkout에서 `git pull --ff-only`, `npm pack`, 새 tarball의 전역 npm 설치를 수행한 뒤 `paper-craft update`를 실행합니다. npm 없이 설치한 경우 갱신한 소스의 Python 설치기에 `--update`를 추가합니다.

`install`은 기존 설치를 덮어쓰지 않습니다. `update`는 현재 실행한 패키지의 Skill을 복사하고 이전 디렉터리를 백업합니다. 결과 JSON에 백업 경로가 표시됩니다. 기본 사용자 설치의 백업은 `~/.agents/paper-craft-backups/`에 저장됩니다. 로컬 수정 사항은 백업에서 검토·병합하세요. 개발 저장소의 원본 Skill과 대상 경로가 겹치면 설치를 거부합니다.

## 사용 예제

원고 경로와 함께 연구 분야, 증거 자료, 목표 Venue·연도·트랙·제출 단계를 제공하세요. 원고 언어를 유지하며, 보고서는 한국어 또는 영어로 요청할 수 있습니다.

```text
$paper-craft 이 아이디어의 Motivation, Failure Mechanism, Insight와 실제 Contribution을 구분해줘.

$paper-craft main.tex의 전체 논증 지도와 섹션별·문단별 개선 Outline을 작성해줘.

$paper-craft main.tex를 기술적 의미를 보존하며 학술 영어로 퇴고해줘. 먼저 수정안·근거·Diff를 보여줘.

$paper-craft 이 Accelerator 논문의 Baseline 공정성과 Claim–Evidence Matrix를 작성해줘.

$paper-craft main.tex를 ISCA 2026 research submission 기준으로 검토해줘. 공식 지침을 확인하고 제출 전 검사 결과를 구분해줘.

$paper-craft IEEE CAL continuing letter submission에 맞는 압축안을 제시해줘. 기여·실험 조건·한계를 보존해줘.

$paper-craft 목표 학회 관점에서 가상 리뷰와 심사 답변 준비안을 작성해줘.
```

## 지원하는 작업

| 작업 | 주요 결과 |
| --- | --- |
| Research Design | 연구 질문, 문제·Research Gap, 설계 가설, 검증 계획 |
| Paper Architect | Argument Map, 섹션 역할, Paragraph-level Outline |
| Novelty Audit | 설계 근거, 가까운 선행연구·단순 대안 비교, 입증된 기여와 미검증 항목 |
| Evidence Audit | Claim–Evidence Matrix, 수치·실험 조건·불확실성·일반화 범위 검토 |
| Academic Editor | 논리·구조·언어 순서의 수정안, 근거, 의미 위험, Unified Diff |
| Reviewer Simulation | 우선순위별 지적, 기술 질문, 추가 실험, 심사 대응 준비 |
| Venue Advisor | 정확한 대상 프로파일, 공식 규정과 작성 권고 구분 |
| Submission Preflight | LaTeX·인용·경로 검사, 제출 형식과 수동 확인 항목 |

Architecture 지침은 프로세서·메모리·가속기·컴파일러와 HW/SW co-design을 다룹니다. 실측, RTL, cycle model, 분석 모델, 추정치를 구분합니다. Systems 지침은 OS·분산·스토리지·네트워크·ML 시스템과 운영 경험을 다루며 설계·통합·구현·측정·운영 기여도 검토합니다.

신규성은 비교 근거와 불확실성으로 설명합니다. 실험 결과나 참고문헌을 생성하지 않으며, 가상 리뷰를 실제 심사나 채택 확률로 제시하지 않습니다.

## 원고와 수정 모드

LaTeX 프로젝트, `.tex`, `.bib`, Markdown, plain text를 지원합니다. PDF는 호스트에 추출·렌더 도구가 있을 때, DOCX는 적절한 문서 도구가 있을 때 검토합니다. 읽지 못한 파일이나 수행할 수 없는 검사는 명시합니다.

| 모드 | 동작 |
| --- | --- |
| Review Only | 기본 모드. 진단 보고서만 작성 |
| Suggest Edits | 원문·수정안·근거·의미 위험·Diff 제시 |
| Apply Approved Edits | 승인된 수정만 실제 파일에 적용 |

수치·단위·수식 의미·Citation Key·LaTeX Label을 보존합니다. 의미나 주장 범위가 달라지는 수정은 별도로 표시합니다. 연구 설계나 실험 결함은 문장 교정으로 감추지 않고 검증 과제로 분류합니다.

## Venue 지원 범위

16개 Venue의 연도·트랙·단계별 캐시 프로파일 18개를 제공합니다.

- Architecture: ISCA, MICRO, HPCA, ASPLOS, PACT, IEEE CAL, IEEE TC, ACM TACO
- Systems: SOSP, OSDI, EuroSys, USENIX ATC, NSDI, ACM TOCS, IEEE TPDS
- 관련 분야: MLSys

프로파일은 부분적으로 검증되어 있습니다. TC·TACO·TOCS·TPDS의 공식 규칙은 현재 UNKNOWN입니다. 지원 Venue가 모든 연도·트랙·제출 단계를 포함한다는 의미는 아닙니다. 캐시의 검증일은 과거 확인 기록이며, 투고 시에는 정확한 대상의 공식 지침을 다시 확인합니다.

공식 규정과 독립적인 연구 방법론·스타일 권고를 구분합니다. 오프라인 검토에서는 현행 규정 준수 여부를 UNKNOWN으로 유지합니다. 확인되지 않은 분량·Appendix·익명화·AI 정책을 추정하지 않습니다.

세부 범위와 출처: [Registry](.agents/skills/paper-craft/venues/registry.json), [Venue Guide](.agents/skills/paper-craft/references/venues/README.md), [공식 출처 목록](.agents/skills/paper-craft/references/venues/sources.md).

## 로컬 검사 도구

다음 예시는 기본 사용자 설치 기준입니다. 프로젝트 로컬 설치라면 `PAPER_CRAFT`를 해당 Skill 디렉터리로 지정합니다.

```bash
PAPER_CRAFT="$HOME/.agents/skills/paper-craft"

python3 "$PAPER_CRAFT/scripts/latex_integrity_check.py" /path/to/main.tex --json
python3 "$PAPER_CRAFT/scripts/reference_audit.py" /path/to/main.tex --json
python3 "$PAPER_CRAFT/scripts/editing_guard.py" /path/to/original.tex /path/to/proposed.tex --json
python3 "$PAPER_CRAFT/scripts/venue_preflight.py" /path/to/main.tex \
  --venue ISCA --year 2026 --track research --stage submission --offline --json
```

스크립트는 기본적으로 읽기 전용이며 네트워크·원고 업로드 기능이 없습니다. Agent 호스트의 데이터 처리 설정은 사용하는 환경을 따릅니다. Python 도구는 표준 라이브러리만 사용합니다.

LaTeX 빌드는 명시적으로 `--build`를 지정한 경우 임시 복사본에서 실행하며 `latexmk`·TeX 배포판이 필요합니다. PDF 페이지 검사는 `pdfinfo`가 있을 때 수행합니다. 누락된 도구는 SKIPPED, 판단 불가는 UNKNOWN, 발견된 위반은 FAIL로 보고합니다. PASS는 실제 수행한 검사 범위에 한정되며, 종료 코드 0도 전체 제출 준비 완료를 뜻하지 않습니다.

매크로·조건부 TeX와 복잡한 bibliography 구조, 인용 진위, 기술적 의미, 렌더링·익명화·최종 제출 정책은 추가 도구 또는 연구자 확인이 필요합니다.

## 참고자료 추가

원본은 작업 저장소의 `source-materials/` 또는 별도 로컬 경로에 보관합니다. 원본 자료가 없어도 핵심 Skill은 동작합니다. HTML은 스크립트를 실행하지 않고 정적으로 추출합니다.

```bash
python3 "$PAPER_CRAFT/scripts/source_material.py" inspect \
  /path/to/reference.html --source-id B --json
```

출력의 SHA-256·행·섹션 위치를 기록하고 `$paper-craft`에 원본 경로와 함께 관련 source guide 갱신을 요청합니다. 실제 원문, 자료 기반 해석, 독립적으로 추가한 지침을 구분하세요. 원본 해시가 바뀌면 근거 위치를 다시 확인합니다. 원본 파일은 자동으로 패키지에 포함하지 않습니다.

해석 범위: [Source Guide](.agents/skills/paper-craft/references/core/source-guides.md). 저장소 입력 절차: [source-materials 안내](https://github.com/code0-god/paper-craft/blob/main/source-materials/README.md).

## 개발과 검증

저장소 checkout에서 실행합니다.

```bash
npm ci --ignore-scripts --no-audit --no-fund
npm run check
npm test
npm run test:python
python3 .agents/skills/paper-craft/scripts/validate_skill.py --json
python3 .agents/skills/paper-craft/scripts/validate_profiles.py --json
```

npm 설치·업데이트·백업 검증과 Python 정적 검사 테스트를 제공합니다. AI 의미 검토는 별도의 [재현 시나리오](https://github.com/code0-god/paper-craft/blob/main/tests/scenarios/README.md)로 확인합니다. 실제 실행 범위는 [검증 기록](https://github.com/code0-god/paper-craft/blob/main/tests/VERIFICATION.md)에 있습니다. 이 개발 자료는 npm 배포물에 포함되지 않습니다.

버그와 사용 중 발견한 문제는 [GitHub Issues](https://github.com/code0-god/paper-craft/issues)에 기록할 수 있습니다.

## 라이선스

[MIT](LICENSE). 독립 Skill에도 동일한 [라이선스 사본](.agents/skills/paper-craft/LICENSE)이 포함됩니다. 외부 참고자료 원본의 권리는 각 권리자에게 있으며, 이 프로젝트의 MIT 라이선스로 재라이선스하지 않습니다.
