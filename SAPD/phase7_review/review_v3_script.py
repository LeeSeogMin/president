"""
Phase 7 v3: 다중 LLM 리뷰 스크립트
paper_draft_v3.md를 GPT-5.2, Grok-4, Claude Sonnet 4.6에 동시 전송하여 리뷰 수행
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

PAPER_PATH = Path(__file__).parent.parent / "phase6_drafting" / "paper_draft_v3.md"
OUTPUT_DIR = Path(__file__).parent / "reviews_v3"

REVIEW_PROMPT = """당신은 한국행정학보 심사위원입니다. 아래 논문을 심사하고 다음 형식으로 상세한 리뷰를 작성해 주십시오.

## 심사 결과
- 판정: [게재 가능 / 수정 후 게재(Minor) / 수정 후 재심(Major) / 게재 불가]

## 총평 (200자 이내)

## 주요 강점 (3-5개)

## 주요 약점 및 수정 요구사항 (5-10개, 구체적으로)

## 세부 코멘트 (절별)

### 서론
### 이론적 배경
### 이재명 정부의 적응형 행정 (§3)
### 연구 방법론
### 상태 기반 적응형 정책 (§5)
### SAPD Framework (§6)
### 이중 타당성 분석 (§7)
### 논의 (§8)
### 결론

## 참고문헌 검토

## 추가 권고사항

심사 시 특히 다음 사항에 유의해 주십시오:
1. 이재명 정부를 직접 분석 대상으로 명시한 것의 학술적 적절성
2. "리더십에서 아키텍처로" 논증의 설득력
3. 정치적 편향 우려에 대한 대응의 충분성
4. SAPD의 이론적 독창성 논증
5. 한국 행정학 문맥에서의 투고 적합성

---

논문:

"""

paper_text = PAPER_PATH.read_text(encoding="utf-8")


async def review_gpt():
    """GPT-5.2 리뷰"""
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    print("[GPT-5.2] 리뷰 요청 시작...")
    resp = await client.chat.completions.create(
        model="gpt-5.2",
        messages=[{"role": "user", "content": REVIEW_PROMPT + paper_text}],
        max_completion_tokens=8192,
        temperature=0.3,
    )
    result = resp.choices[0].message.content
    out = OUTPUT_DIR / "review_gpt5.2_v3.md"
    out.write_text(f"# GPT-5.2 리뷰 (v3)\n\n{result}", encoding="utf-8")
    print(f"[GPT-5.2] 리뷰 완료 → {out}")
    return result


async def review_grok():
    """Grok-4 리뷰"""
    from openai import AsyncOpenAI
    client = AsyncOpenAI(
        api_key=os.getenv("XAI_API_KEY"),
        base_url="https://api.x.ai/v1",
    )
    print("[Grok-4] 리뷰 요청 시작...")
    resp = await client.chat.completions.create(
        model="grok-4-1-fast-reasoning",
        messages=[{"role": "user", "content": REVIEW_PROMPT + paper_text}],
        max_tokens=8192,
        temperature=0.3,
    )
    result = resp.choices[0].message.content
    out = OUTPUT_DIR / "review_grok4_v3.md"
    out.write_text(f"# Grok-4 리뷰 (v3)\n\n{result}", encoding="utf-8")
    print(f"[Grok-4] 리뷰 완료 → {out}")
    return result


async def review_claude():
    """Claude Sonnet 4.6 리뷰"""
    import anthropic
    client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    print("[Claude Sonnet 4.6] 리뷰 요청 시작...")
    resp = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        messages=[{"role": "user", "content": REVIEW_PROMPT + paper_text}],
    )
    result = resp.content[0].text
    out = OUTPUT_DIR / "review_claude_sonnet_v3.md"
    out.write_text(f"# Claude Sonnet 4.6 리뷰 (v3)\n\n{result}", encoding="utf-8")
    print(f"[Claude Sonnet 4.6] 리뷰 완료 → {out}")
    return result


async def main():
    print("=" * 60)
    print("Phase 7 v3: 다중 LLM 리뷰 시작")
    print("=" * 60)
    results = await asyncio.gather(
        review_gpt(),
        review_grok(),
        review_claude(),
        return_exceptions=True,
    )
    print("\n" + "=" * 60)
    for name, r in zip(["GPT-5.2", "Grok-4", "Claude Sonnet 4.6"], results):
        if isinstance(r, Exception):
            print(f"[{name}] 오류: {r}")
            err_file = OUTPUT_DIR / f"error_{name.lower().replace(' ', '_')}_v3.txt"
            err_file.write_text(str(r), encoding="utf-8")
        else:
            print(f"[{name}] 성공 ({len(r)}자)")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
