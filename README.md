# Paper Craft

Computer Architecture / Computer Systems 연구용 설치형 Agent Skill. 연구 설계, 논증 구조, 신규성, 실험 근거, 학술 퇴고, 가상 심사, Venue 검토, 제출 전 검사를 지원합니다. 서버·MCP·웹 서비스 없이 파일과 지침으로 동작합니다.

Canonical 패키지: [`.agents/skills/paper-craft/SKILL.md`](.agents/skills/paper-craft/SKILL.md). 이 디렉터리 전체만 복사해 사용할 수 있습니다. 원본 논문·첨부자료·테스트 디렉터리는 설치에 필요하지 않습니다.

## 환경과 설치

Codex CLI 또는 Agent Skills 표준을 지원하는 호스트에서 사용합니다. 핵심 연구 검토는 호스트 모델이 수행합니다. 정적 검사 도구는 Python 3.10+ 표준 라이브러리만 필요합니다. LaTeX 빌드는 `latexmk`와 TeX 배포판, PDF 페이지 검사는 `pdfinfo`, PDF 텍스트 분석은 `pdftotext` 등 가용 도구가 있을 때만 수행합니다. DOCX는 호스트에 문서 추출 도구가 있을 때 지원하며, 미설치 기능은 `SKIPPED`로 보고합니다.

Codex 프로젝트 로컬 발견 경로는 `.agents/skills`, 사용자 경로는 `~/.agents/skills`입니다. 프로젝트 루트에서 Codex를 실행하고 `/skills` 또는 `$paper-craft`로 선택합니다. 변경이 보이지 않으면 세션을 다시 시작합니다. [공식 Codex Skill 문서](https://learn.chatgpt.com/docs/build-skills)

현재 저장소에서 바로 사용:

```bash
cd /path/to/paper-craft
python3 .agents/skills/paper-craft/scripts/validate_skill.py --json
codex
```

다른 프로젝트에서 사용하도록 사용자 범위에 설치:

```bash
python3 .agents/skills/paper-craft/scripts/install_skill.py \
  --destination "$HOME/.agents/skills/paper-craft"
```

다른 저장소의 프로젝트 로컬 설치:

```bash
python3 .agents/skills/paper-craft/scripts/install_skill.py \
  --destination /path/to/research-repo/.agents/skills/paper-craft
```

수동 설치도 가능합니다. 대상이 없는지 먼저 확인하고 디렉터리 전체를 복사합니다. 심볼릭 링크에 의존하지 않습니다.

```bash
mkdir -p "$HOME/.agents/skills"
cp -R .agents/skills/paper-craft "$HOME/.agents/skills/paper-craft"
```

이미 설치되어 있다면 수동 덮어쓰기 대신 아래 업데이트 명령을 사용합니다. Git 업데이트는 기존 사용자 변경을 보존할 수 있는 `git pull --ff-only`로 수행합니다.

```bash
git pull --ff-only
python3 .agents/skills/paper-craft/scripts/install_skill.py \
  --destination "$HOME/.agents/skills/paper-craft" --update
```

설치기는 기존 대상이 있으면 기본적으로 거부합니다. `--update`는 이전 디렉터리를 보존하고 새 패키지로 교체합니다. `skills/` 아래 설치의 백업은 그 상위 디렉터리의 `paper-craft-backups/`에 저장하여 중복 스킬 발견을 피합니다. 로컬 수정 사항은 백업에서 검토·병합하십시오.

GitHub Skill Installer 사용:

```text
$skill-installer https://github.com/code0-god/paper-craft/tree/main/.agents/skills/paper-craft
Install into ~/.agents/skills, preserving the complete paper-craft directory.
```

Git 원격은 `git@github.com:code0-god/paper-craft.git`, 브랜치는 `main`입니다. GitHub 설치는 해당 커밋이 원격에 올라간 뒤 사용할 수 있습니다. 재현 가능한 설치에는 `--ref`에 특정 커밋을 지정합니다. Installer CLI가 설치되어 있다면 다음 형태로 실행할 수 있습니다. `INSTALLER`는 해당 환경의 실제 `install-skill-from-github.py` 경로입니다.

```bash
python3 "$INSTALLER" --repo code0-god/paper-craft --ref main \
  --path .agents/skills/paper-craft --dest "$HOME/.agents/skills"
```

## 호출 예제

원고 경로, 증거 자료, 대상 Venue·연도·트랙·단계를 함께 제공하면 검토 범위가 명확해집니다. 원고 언어는 임의로 바꾸지 않으며 보고서 언어는 요청할 수 있습니다.

```text
$paper-craft 이 연구 아이디어가 Motivation 수준인지 실제 Novelty인지 검토해줘.
$paper-craft main.tex의 서론부터 결론까지 논증 구조와 개선된 Outline을 작성해줘.
$paper-craft main.tex를 기술적 의미를 보존하며 학술 영어로 퇴고해줘. 먼저 수정안과 Diff를 보여줘.
$paper-craft 이 Accelerator Architecture 논문의 설계 근거, Baseline, 실험 평가를 검토해줘.
$paper-craft main.tex를 ISCA 2026 research submission 기준으로 리뷰해줘. 공식 지침을 재확인해줘.
$paper-craft IEEE CAL continuing letter submission에 맞춰 압축안을 제시해줘. 기여와 근거를 보존해줘.
$paper-craft 목표 학회 심사자 관점에서 비판적으로 평가하고 심사 대응 준비를 도와줘.
```

공통 결과에는 위치·심각도·근거·해석·수정 방향·추가 실험·검증 상태가 포함됩니다. 신규성은 절대 점수로 판정하지 않습니다. 가상 심사는 공식 평가나 채택 확률 예측이 아닙니다.

## 기능과 원본 보존

- Research Design: 연구 질문·문제·Failure Mechanism·Research Gap·가설·검증 계획.
- Paper Architect: 전체 Argument Map, 섹션의 질문/주장/근거/연결, Paragraph-level Outline.
- Novelty Audit: Motivation–Challenge–Insight–Method–Contribution 연결, 가장 가까운 선행연구·단순 대안·Ablation 검토.
- Evidence Audit: Claim–Evidence Matrix, 수치·조건·Baseline·불확실성·일반화 범위·인과 해석 검토.
- Academic Editor: 논리, 구조, 언어 순서의 퇴고; 영문·국문 지원.
- Reviewer Simulation: Critical/Major/Minor/Suggestion 분류, 기술 질문·수정 방향·심사 대응.
- Venue Advisor: 정확한 Venue/연도/트랙/단계 프로파일, 공식 규정과 독립 권고 분리.
- Submission Preflight: LaTeX 무결성·인용·경로·템플릿 정적 검사, 수동 제출 체크.

Architecture 지침은 프로세서·메모리·병렬·가속기·DNN/LLM·양자화·FPGA/ASIC·컴파일러·HW/SW co-design을 다룹니다. 측정·RTL·cycle model·분석 모델·추정치를 분리합니다. Systems 지침은 OS·분산·스토리지·네트워크·클라우드·런타임·자원관리·스케줄링·ML 시스템·운영 경험을 다룹니다. 알고리즘 외 설계·통합·측정·운영 기여도 인정합니다.

기본 모드는 **Review Only**. 수정안 요청은 **Suggest Edits**. 실제 파일 적용은 **Apply Approved Edits**이며 승인된 수정만 적용합니다. 원본 스냅샷/버전관리 기준, Unified Diff, 수정 근거 기록을 유지합니다. 수치·단위·수식·인용키·Label 보존 검사와 수동 의미 검토를 함께 사용합니다. 논리나 실험 결함을 문장 교정으로 감추지 않습니다.

## 검사 도구

`PAPER_CRAFT`는 현재 설치 디렉터리입니다. 아래 명령은 원고를 읽기 전용으로 검사합니다.

```bash
PAPER_CRAFT="$PWD/.agents/skills/paper-craft"
python3 "$PAPER_CRAFT/scripts/latex_integrity_check.py" /path/to/main.tex --json
python3 "$PAPER_CRAFT/scripts/reference_audit.py" /path/to/main.tex --json
python3 "$PAPER_CRAFT/scripts/editing_guard.py" /path/to/original.tex /path/to/proposed.tex --json
python3 "$PAPER_CRAFT/scripts/validate_profiles.py" --json
python3 "$PAPER_CRAFT/scripts/venue_preflight.py" /path/to/main.tex \
  --venue ISCA --year 2026 --track research --stage submission --offline --json
```

LaTeX 빌드를 요청한 경우에만 `latex_integrity_check.py --build`를 사용합니다. 임시 복사본에서 shell escape를 끄고 실행합니다. 이것은 OS sandbox가 아니므로 신뢰할 수 없는 프로젝트를 실행하지 않습니다. 정적 검사에는 실행·원격 업로드·네트워크 요청이 없습니다.

JSON 상태: `PASS`는 실제 수행한 해당 검사 통과, `FAIL`은 발견된 위반, `SKIPPED`는 미실행/지원 부족, `UNKNOWN`은 판단 불가. 종료 코드 0은 검사 보고서 생성 성공이며 전체 제출 적합성 보증이 아닙니다. 1은 검출된 실패, 2는 잘못된 입력/사용법입니다. 보고서 내부 항목을 함께 확인하십시오. 정적 TeX 분석은 매크로 확장·동적 경로·모든 패키지 동작을 해석하지 않습니다.

## Venue Intelligence

16개 우선 Venue: ISCA, MICRO, HPCA, ASPLOS, PACT, SOSP, OSDI, EuroSys, USENIX ATC, NSDI, MLSys, IEEE CAL, IEEE TC, ACM TACO, ACM TOCS, IEEE TPDS. Registry와 버전별 JSON은 [`venues/`](.agents/skills/paper-craft/venues/registry.json)에 있습니다.

공식 CFP·Author Instructions를 실제 확인한 규정에 출처 URL, 출처 종류, 검증일, 적용 범위와 상태를 저장합니다. 상태는 `verified`, `unverified`, `outdated`, `conflicting`. 확인하지 못한 분량·Appendix·AI 정책은 `null`/`UNKNOWN`입니다. 프로파일 선택은 연도·트랙·단계까지 일치해야 합니다. Conference의 과거 연도를 새 연도에 적용하지 않으며, journal의 continuing 지침도 최신 확인이 필요합니다.

프로파일 검증과 현재 투고 규정 검증은 다릅니다. 로컬 preflight는 네트워크를 사용하지 않습니다. 캐시만으로 현재 적용 가능성을 확정하지 않고 `UNKNOWN`과 재확인 항목을 보고합니다. 온라인 검토에서는 Agent가 공식 출처를 다시 읽고 관련 규칙을 갱신합니다. 실제 페이지 수·익명화·정책 준수·Artifact 준비 등 자동 확정이 어려운 항목은 수동 확인합니다. 갱신 절차·우선순위·규칙별 상태는 [Venue 가이드](.agents/skills/paper-craft/references/venues/README.md)를 따릅니다.

## 참고자료 A/B

`source-materials/`는 로컬 입력 위치입니다. 원본 파일·추출 텍스트·개인 경로는 Git에 자동 포함하지 않으며 배포 설치에도 포함하지 않습니다. 저작권 확인 없이 원문을 복제·배포하지 않습니다.

- A: [Motivation ≠ Novelty](https://gisbi-kim.github.io/motivation-is-not-novelty/) 웹 원문 확인 기반. 직접 첨부 파일은 아직 제공되지 않았습니다. 사례·휴리스틱을 보편적 합격 조건으로 만들지 않습니다.
- B: 제공된 `논문_논리적_글쓰기.html`을 HTMLParser로 안전하게 읽었습니다. source guide에 제목·해시·HTML 위치와 짧은 해석을 기록합니다. 원본은 Downloads에 보존됩니다.

후속 첨부자료 반영:

1. A/B 원본을 로컬 `source-materials/`로 복사하거나 기존 로컬 경로를 지정합니다. HTML은 열어 실행하지 않습니다.
2. 정적 추출 보고서를 생성합니다. 원본을 수정하지 않으며 source ID·SHA256·형식·행/블록 위치를 기록합니다.

```bash
python3 .agents/skills/paper-craft/scripts/source_material.py inspect \
  /path/to/reference.html --source-id B --json
```

3. `$paper-craft`에 이 보고서와 원본 경로를 제공하고 source guide 갱신을 요청합니다. 원문에 명시된 내용, 자료 기반 해석, 독립 연구 지침을 구분하고 기존 해시와 비교합니다. 자료에 없는 내용은 자료 주장으로 적지 않습니다.
4. 새 원문을 실제 읽은 뒤 [source guide](.agents/skills/paper-craft/references/core/source-guides.md)의 상태·근거 위치·날짜를 수정합니다. 패키지 검증과 관련 시나리오를 다시 실행합니다.

자료가 없어도 설치·핵심 워크플로는 동작합니다. 세부 입력 절차는 [source-materials/README.md](source-materials/README.md)를 따릅니다.

## 테스트와 검증

표준 라이브러리 자동 테스트:

```bash
python3 -m unittest discover -s tests -v
python3 .agents/skills/paper-craft/scripts/validate_skill.py --json
python3 .agents/skills/paper-craft/scripts/validate_profiles.py --json
```

개발용 lint/typecheck 도구가 있으면 다음을 실행합니다. 스킬 런타임에는 이 도구가 필요하지 않습니다. 저장소에 새 런타임 의존성을 추가하지 않았습니다.

```bash
ruff check .agents/skills/paper-craft/scripts tests
basedpyright
```

호스트의 스킬 발견 목록은 지원되는 Codex 버전에서 다음으로 확인할 수 있습니다. 이 명령은 의미 검토 실행 테스트가 아닙니다. 출력에는 사용자 설정이 포함될 수 있으므로 원본 출력 전체를 공유하지 않습니다.

```bash
codex debug prompt-input '$paper-craft Review this architecture research idea.'
```

명시 호출의 실제 검토 실행은 Codex 대화에서 예제 프롬프트를 입력하거나 read-only CLI로 확인합니다.

```bash
codex exec --ephemeral --sandbox read-only \
  '$paper-craft Review this idea: memory traffic slows inference; combine a cache and prefetcher; no experiments or closest-work comparison yet. Do not edit files.'
```

AI 의미 검토는 unit test가 대신 증명하지 않습니다. [시나리오](tests/scenarios/README.md)에 재현 입력·프롬프트·기대 검토 기준을 제공합니다. 실제 실행 결과와 미실행 검사는 [검증 기록](tests/VERIFICATION.md)에 분리해 기록합니다.

## 핵심 구조

```text
.agents/skills/paper-craft/
  SKILL.md                 발견·모드·라우팅·안전 규칙
  agents/openai.yaml       UI 메타데이터·자동 호출 정책
  references/core/         논증·신규성·근거·출처 가이드
  references/domains/      Architecture·Systems·HW/SW co-design
  references/workflows/    연구·구조·퇴고·심사·입력·제출 절차
  references/venues/       공식 규정·캐시·갱신 절차
  venues/                  Registry·연도/트랙/단계별 프로파일
  schemas/                 Venue·검토 보고서 스키마
  scripts/                 LaTeX·인용·수정 보존·자료·설치·검증
  assets/                  보고서·근거·수정 추적 템플릿
source-materials/           로컬 원본 입력, 배포 제외
tests/                     자동 테스트·Fixture·의미 검토 시나리오
```

## 한계와 갱신

정적 검사 통과는 연구의 타당성·신규성·기술적 의미 보존이나 최종 채택을 보장하지 않습니다. 의미 평가는 근거를 읽는 Agent와 연구자의 검증이 필요합니다. 수치 비교는 제공된 표·실험 데이터의 범위에 한정됩니다. PDF 그림·페이지 배치, DOCX 레이아웃, 익명화와 제출 사이트 필드는 도구/수동 검토가 필요합니다. 확인 실패한 Venue 규칙은 남아 있을 수 있으며, 투고 시점에 공식 지침을 재확인해야 합니다.

향후 개선은 실제 사용에서 드러난 누락된 TeX 명령, 새 Venue/트랙의 공식 프로파일, 더 다양한 의미 평가 사례부터 추가합니다. 현재 없는 실험 결과나 최신 규정을 추정해 채우지 않습니다.

규격 확인 기준일: 2026-10-08. [Agent Skills specification](https://agentskills.io/specification), [OpenAI Codex 저장소](https://github.com/openai/codex), [Codex Skill 작성 지침](https://learn.chatgpt.com/docs/build-skills).
