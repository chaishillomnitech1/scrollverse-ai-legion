# AURELLION Research Notes and References

**Research snapshot:** 2026-11-12  
**Scope:** Agent architecture, AI risk, provenance, rights, and digital collectible standards. This is a foundation review, not legal advice, security certification, or exhaustive literature review.

## AI governance and risk

1. **NIST AI Risk Management Framework (AI RMF 1.0)** — organizes risk work through Govern, Map, Measure, and Manage. NIST notes the framework is under revision, so check updated profiles and releases before each formal review.  
   https://www.nist.gov/itl/ai-risk-management-framework

2. **NIST AI RMF Generative AI Profile (NIST AI 600-1)** — generative-AI risk profile, including privacy, intellectual-property, security, and information-integrity concerns.  
   https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf

3. **OWASP Top 10 for Agentic Applications 2026** — agent-goal hijack, tool misuse, identity/privilege abuse, supply-chain risks, unexpected code execution, memory/context poisoning, insecure inter-agent communication, cascading failures, human-agent trust exploitation, and rogue agents.  
   https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/

4. **OWASP GenAI LLM Top 10 2026** — use the latest release to map LLM-specific risks at feature design and review time.  
   https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/

## Rights and naming

5. **U.S. Copyright Office — Copyright and Artificial Intelligence, Part 2: Copyrightability** — assess human authorship, selection, arrangement, and modification; AI-assisted copyright questions are fact-specific.  
   https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf

6. **USPTO trademark search** — an exact internet or repository name search is not trademark clearance. Search similar marks, goods/services, common-law uses, and relevant jurisdictions with counsel.  
   https://www.uspto.gov/trademarks/search

7. **OpenAI brand guidelines** — avoid implying sponsorship, endorsement, or ownership by a model provider; describe model/provider use factually.  
   https://openai.com/brand/

## Digital collectible standards

8. **ERC-721** — non-fungible token interface.  
   https://eips.ethereum.org/EIPS/eip-721

9. **ERC-1155** — multi-token standard for multiple token types.  
   https://eips.ethereum.org/EIPS/eip-1155

10. **EIP-2981** — royalty-information interface; marketplace payment is not guaranteed by the standard alone.  
    https://eips.ethereum.org/EIPS/eip-2981

## Engineering implications

- Use least privilege, explicit tool allowlists, human confirmation for consequential actions, budgets, rate limits, timeouts, and a kill switch.
- Keep model/provider identity explicit and replaceable.
- Separate source text from instructions and treat retrieved material as untrusted.
- Evaluate retrieval provenance, tool correctness, prompt-injection resistance, privacy leakage, refusal behavior, and recovery/rollback.
- Preserve source originals; record raw-file SHA-256 separately from Git blob SHA, commit SHA, UUID, and chain transaction hash.
- Maintain human review of generated code and all security-critical changes.
- For digital collectibles, treat token standards as technical interfaces, not legal guarantees or economic promises.

## Limits

These sources do not establish AURELLION trademark availability, copyright ownership of every artifact, compliance in every jurisdiction, security certification, commercial demand, or any token's value. Those require professional review and project-specific evidence.


## OpenAI model API integration

For new OpenAI integrations, use the Responses API rather than starting new work on the legacy Assistants API. The official migration guide states that the Assistants API was sunset on August 26, 2026 and directs new integrations to Responses. AURELLION's adapter therefore defaults to the explicit Responses API style; Chat Completions remains an opt-in compatibility mode for providers that expose that contract.

- OpenAI API overview and Responses quickstart: https://platform.openai.com/overview
- Assistants migration guide: https://platform.openai.com/playground/assistants

AURELLION sends application-managed message history as Responses input and sets store=false. The provider adapter remains replaceable; this does not connect a provider or authorize live requests.


## GitHub Copilot reusable agents and skills

GitHub documents repository custom agents under .github/agents and repository agent skills under .github/skills/<skill-name>/SKILL.md. Skills can be loaded when relevant by supported Copilot surfaces. Custom agent profiles can restrict their tool access; the AURELLION GitHub guide therefore explicitly permits only read and search tools.

- GitHub Copilot customization cheat sheet: https://docs.github.com/en/copilot/reference/customization-cheat-sheet
- Custom agent configuration and tool restrictions: https://docs.github.com/en/copilot/reference/custom-agents-configuration
- Adding agent skills: https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills
- GitHub Copilot app customization: https://docs.github.com/en/copilot/how-tos/github-copilot-app/customize-github-copilot-app

These repository assets become available after the PR is merged into the default branch and the user's Copilot surface supports the feature. They do not create an anonymous public chatbot or grant access to private repositories beyond the host's existing token scope.
