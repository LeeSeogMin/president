"""
Phase 7: Multi-LLM Academic Paper Review
3개 LLM(GPT-5.2, Grok-4, Claude Sonnet 4.6)을 사용한 학술 논문 리뷰
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Load .env manually
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

import openai
import anthropic
import httpx

# Read paper
paper_path = Path(__file__).parent.parent / "phase6_drafting" / "paper_draft_v1.md"
PAPER = paper_path.read_text(encoding="utf-8")

REVIEW_PROMPT = """당신은 한국행정학보(Korean Public Administration Review) 심사위원입니다.
아래 논문을 학술 심사 기준에 따라 정밀하게 리뷰해 주십시오.

## 심사 기준
1. **독창성 및 학술적 기여**: 기존 문헌 대비 새로운 기여가 명확한가?
2. **논증의 논리적 정합성**: 4개 명제(P1-P4)의 논증 흐름이 일관되고 설득력 있는가?
3. **이론적 엄밀성**: 핵심 개념(상태 변수, 의사결정 함수, 피드백 루프)의 정의가 명확한가?
4. **선행연구 검토의 충실도**: 관련 문헌이 충분히 검토되었는가? 누락된 핵심 문헌이 있는가?
5. **팔란티어 구조적 동형성 분석의 타당성**: 민간 플랫폼과의 비교가 학술적으로 적절한가?
6. **실행 가능성과 한계 인식**: 프레임워크의 적용 조건과 한계가 충분히 논의되었는가?
7. **국문 학술 작문 품질**: 문장이 명확하고 학술적 격식을 갖추었는가?
8. **구조와 분량**: 논문의 구조가 체계적이며 각 섹션의 분량이 균형 잡혔는가?

## 출력 형식
다음 형식으로 리뷰를 작성해 주십시오:

### 1. 총평 (Overall Assessment)
[게재 가능 / 수정 후 게재 / 수정 후 재심 / 게재 불가 중 판정]

### 2. 강점 (Strengths)
- [구체적 강점 5개 이상]

### 3. 약점 및 개선 요구 사항 (Weaknesses & Required Revisions)
- [구체적 약점 및 수정 사항 5개 이상, 각각에 대해 구체적 수정 방향 제시]

### 4. 세부 코멘트 (Detailed Comments)
[섹션별 구체적 코멘트]

### 5. 누락된 문헌 또는 논점 (Missing References/Arguments)
[추가해야 할 문헌이나 논점]

### 6. 수정 우선순위 (Revision Priority)
[가장 시급한 수정 사항 3개를 우선순위 순으로]

---
[논문 전문]

""" + PAPER


async def review_openai():
    """GPT-5.2 리뷰"""
    print("[GPT-5.2] 리뷰 시작...")
    client = openai.AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    try:
        response = await client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o"),
            messages=[{"role": "user", "content": REVIEW_PROMPT}],
            max_completion_tokens=8192,
            temperature=0.3,
        )
        result = response.choices[0].message.content
        print(f"[GPT-5.2] 리뷰 완료 ({len(result)} chars)")
        return result
    except Exception as e:
        print(f"[GPT-5.2] 오류: {e}")
        return f"[GPT-5.2 리뷰 실패]\n오류: {e}"


async def review_grok():
    """Grok-4 리뷰 (xAI API - OpenAI-compatible)"""
    print("[Grok-4] 리뷰 시작...")
    client = openai.AsyncOpenAI(
        api_key=os.environ.get("XAI_API_KEY"),
        base_url="https://api.x.ai/v1",
    )
    try:
        response = await client.chat.completions.create(
            model=os.environ.get("GROK_MODEL", "grok-3"),
            messages=[{"role": "user", "content": REVIEW_PROMPT}],
            max_tokens=int(os.environ.get("GROK_MAX_TOKENS", "8192")),
            temperature=float(os.environ.get("GROK_TEMPERATURE", "0.3")),
        )
        result = response.choices[0].message.content
        print(f"[Grok-4] 리뷰 완료 ({len(result)} chars)")
        return result
    except Exception as e:
        print(f"[Grok-4] 오류: {e}")
        return f"[Grok-4 리뷰 실패]\n오류: {e}"


async def review_claude():
    """Claude Sonnet 4.6 리뷰"""
    print("[Claude Sonnet 4.6] 리뷰 시작...")
    client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    try:
        response = await client.messages.create(
            model=os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6"),
            max_tokens=8192,
            messages=[{"role": "user", "content": REVIEW_PROMPT}],
        )
        result = response.content[0].text
        print(f"[Claude Sonnet 4.6] 리뷰 완료 ({len(result)} chars)")
        return result
    except Exception as e:
        print(f"[Claude Sonnet 4.6] 오류: {e}")
        return f"[Claude Sonnet 4.6 리뷰 실패]\n오류: {e}"


async def main():
    print("=" * 60)
    print("Phase 7: Multi-LLM Academic Paper Review")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"논문 크기: {len(PAPER):,} bytes")
    print("=" * 60)

    # Run all 3 reviews in parallel
    results = await asyncio.gather(
        review_openai(),
        review_grok(),
        review_claude(),
        return_exceptions=True,
    )

    models = ["GPT-5.2", "Grok-4", "Claude Sonnet 4.6"]
    output_dir = Path(__file__).parent / "reviews"
    output_dir.mkdir(exist_ok=True)

    for model_name, result in zip(models, results):
        if isinstance(result, Exception):
            result = f"[리뷰 실패]\n오류: {result}"

        filename = f"review_{model_name.lower().replace(' ', '_').replace('.', '')}.md"
        filepath = output_dir / filename

        header = f"# {model_name} 학술 리뷰\n\n"
        header += f"리뷰 일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        header += f"대상 논문: paper_draft_v1.md\n\n---\n\n"

        filepath.write_text(header + result, encoding="utf-8")
        print(f"\n[저장] {filepath}")

    # Synthesize reviews
    print("\n" + "=" * 60)
    print("리뷰 종합 보고서 생성 중...")

    synthesis = "# 다중 LLM 리뷰 종합 보고서\n\n"
    synthesis += f"리뷰 일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    synthesis += f"리뷰 모델: GPT-5.2, Grok-4, Claude Sonnet 4.6\n\n---\n\n"

    for model_name, result in zip(models, results):
        if isinstance(result, Exception):
            result = f"리뷰 실패: {result}"
        synthesis += f"## {model_name} 리뷰\n\n{result}\n\n---\n\n"

    synthesis_path = output_dir / "review_synthesis.md"
    synthesis_path.write_text(synthesis, encoding="utf-8")
    print(f"[저장] {synthesis_path}")

    print("\n" + "=" * 60)
    print(f"완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
