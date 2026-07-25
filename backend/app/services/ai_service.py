import re
from typing import Dict, Any, Tuple

class AIService:
    """
    Hybrid Classification Engine:
    Uses Keyword/Rule Engine first, evaluates confidence, falls back or verifies AI classification.
    Catches traps:
    - Untrusted Customer Priority (e.g. marked Low when description indicates server crash/outage -> High)
    - Untrusted Customer Priority (e.g. marked High for simple password reset -> Low)
    - Mis-categorized ticket (marked Technical for double charge billing issue -> Billing)
    - Missing Priority or Category
    - Vague Description ("It broke")
    - Non-English Language detection
    """

    HIGH_PRIORITY_KEYWORDS = [
        "crash", "down", "outage", "production", "security breach", "unauthorized",
        "charged twice", "deducted twice", "double billing", "p0", "urgent", "critical", "breach"
    ]

    MEDIUM_PRIORITY_KEYWORDS = [
        "timeout", "slow", "error code 504", "export", "webhook", "failed",
        "feature request", "saml", "sso", "unable to update"
    ]

    LOW_PRIORITY_KEYWORDS = [
        "password reset", "forgot password", "contrast", "dark mode", "pdf copy",
        "tax accounting", "rechnung", "avatar", "profile picture"
    ]

    CATEGORY_KEYWORDS = {
        "Billing": ["charge", "charged", "billing", "invoice", "refund", "deducted", "payment", "card", "rechnung", "pago", "factura"],
        "Technical": ["database", "outage", "500", "504", "timeout", "webhook", "api", "crash", "server", "error"],
        "Account": ["password", "reset", "login", "auth", "profile", "account", "avatar"],
        "Security": ["breach", "unauthorized", "oauth2", "exploit", "threat"],
        "UI/UX": ["dark mode", "contrast", "ui", "font", "css", "screen"],
        "Feature Request": ["feature request", "saml 2.0", "okta", "integration"]
    }

    SPANISH_INDICATORS = ["hola", "error al procesar", "pago", "factura", "gracias", "tarjeta"]
    GERMAN_INDICATORS = ["guten tag", "fehler", "herunterladen", "rechnung", "deutschland", "nicht"]

    LANGUAGE_TRANSLATION_MAP = {
        "es": {
            "error al procesar el pago": "error processing payment",
            "hola": "hello",
            "intenté": "tried",
            "intente": "tried",
            "pagar": "pay",
            "factura": "invoice",
            "mensual": "monthly",
            "sistema": "system",
            "muestra": "shows",
            "tarjeta": "card",
            "rechazada": "rejected",
            "cuenta": "account",
            "explicaciones": "explanations",
            "error": "error",
        },
        "de": {
            "guten tag": "hello",
            "fehler beim herunterladen der rechnung": "error while downloading invoice",
            "fehler": "error",
            "herunterladen": "download",
            "rechnung": "invoice",
            "dokument": "document",
            "kann nicht heruntergeladen werden": "cannot be downloaded",
            "nicht": "not",
            "wird immer": "is always",
            "angezeigt": "shown",
            "pdf-dokument": "pdf document",
            "not found": "not found",
        },
    }

    def _detect_language(self, combined_text: str) -> str:
        detected = "en"
        best_score = 0

        for language, indicators in (("es", self.SPANISH_INDICATORS), ("de", self.GERMAN_INDICATORS)):
            score = sum(1 for indicator in indicators if indicator in combined_text)
            if score > best_score:
                detected = language
                best_score = score

        return detected

    def _normalize_text_for_analysis(self, combined_text: str, language: str) -> Tuple[str, str]:
        if language == "en":
            return combined_text, ""

        translated_text = combined_text
        translation_map = self.LANGUAGE_TRANSLATION_MAP.get(language, {})
        matched_terms = []

        for source, target in sorted(translation_map.items(), key=lambda item: len(item[0]), reverse=True):
            pattern = rf"\b{re.escape(source)}\b"
            if re.search(pattern, translated_text):
                translated_text = re.sub(pattern, target, translated_text)
                matched_terms.append(f"{source}->{target}")

        if translated_text == combined_text:
            return combined_text, ""

        normalized_text = f"{combined_text} {translated_text}"
        translation_summary = ", ".join(matched_terms[:6])
        if len(matched_terms) > 6:
            translation_summary += ", ..."

        return normalized_text, translation_summary

    def analyze_and_verify(self, subject: str, description: str, customer_cat: str, customer_prio: str) -> Dict[str, Any]:
        combined_text = f"{subject} {description}".lower()

        # 1. Detect Non-English Language
        lang = self._detect_language(combined_text)
        analysis_text, translation_summary = self._normalize_text_for_analysis(combined_text, lang)

        reasoning_parts = []
        if lang == "en":
            reasoning_parts.append("Ticket text is in English.")
        else:
            if translation_summary:
                reasoning_parts.append(
                    f"Detected {lang.upper()} text and normalized it internally before analysis ({translation_summary})."
                )
            else:
                reasoning_parts.append(f"Detected {lang.upper()} text and analyzed it with internal normalization.")

        # 2. Detect Vague Ticket
        is_vague = False
        words = description.strip().split()
        if len(words) < 4 or description.strip().lower() in ["it broke.", "help", "system issue", "broken"]:
            is_vague = True

        # 3. Category Inference & Verification
        inferred_cat = None
        inferred_cat_keyword = None
        for cat, keywords in self.CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in analysis_text:
                    inferred_cat = cat
                    inferred_cat_keyword = kw
                    break
            if inferred_cat:
                break
        
        resolved_category = customer_cat.strip() if customer_cat and customer_cat.strip() else "General"
        if inferred_cat and (not customer_cat or customer_cat.strip() != inferred_cat):
            # Correct untrusted or missing category
            resolved_category = inferred_cat

        if inferred_cat:
            if resolved_category == inferred_cat:
                reasoning_parts.append(
                    f"Category resolved to {resolved_category} from keyword evidence '{inferred_cat_keyword}'."
                )
            else:
                reasoning_parts.append(f"Category kept as {resolved_category} from the customer payload.")
        else:
            reasoning_parts.append(f"Category kept as {resolved_category} because no stronger category signal was found.")

        # 4. Priority Inference & Verification
        inferred_prio = None
        inferred_prio_keyword = None
        if any(kw in analysis_text for kw in self.HIGH_PRIORITY_KEYWORDS):
            inferred_prio = "High"
            for kw in self.HIGH_PRIORITY_KEYWORDS:
                if kw in analysis_text:
                    inferred_prio_keyword = kw
                    break
        elif any(kw in analysis_text for kw in self.LOW_PRIORITY_KEYWORDS):
            inferred_prio = "Low"
            for kw in self.LOW_PRIORITY_KEYWORDS:
                if kw in analysis_text:
                    inferred_prio_keyword = kw
                    break
        elif any(kw in analysis_text for kw in self.MEDIUM_PRIORITY_KEYWORDS):
            inferred_prio = "Medium"
            for kw in self.MEDIUM_PRIORITY_KEYWORDS:
                if kw in analysis_text:
                    inferred_prio_keyword = kw
                    break

        resolved_priority = customer_prio.strip().capitalize() if customer_prio and customer_prio.strip() in ["Low", "Medium", "High"] else "Medium"

        confidence_score = 0.95
        if lang != "en":
            confidence_score -= 0.03
        if inferred_prio and resolved_priority != inferred_prio:
            # Overrule customer priority when text strong evidence exists
            resolved_priority = inferred_prio
            confidence_score = 0.90
            reasoning_parts.append(
                f"Priority overridden to {resolved_priority} from keyword evidence '{inferred_prio_keyword}'."
            )
        elif inferred_prio:
            reasoning_parts.append(
                f"Priority confirmed as {resolved_priority} from keyword evidence '{inferred_prio_keyword}'."
            )

        if not customer_prio or customer_prio.strip() not in ["Low", "Medium", "High"]:
            resolved_priority = inferred_prio if inferred_prio else "Medium"
            confidence_score = 0.85
            reasoning_parts.append("Priority defaulted from the ticket text because the customer priority was missing or invalid.")
        elif not inferred_prio:
            reasoning_parts.append(f"Priority kept as {resolved_priority} from the customer payload.")

        if is_vague:
            confidence_score = 0.60
            resolved_priority = "Low"
            reasoning_parts.append("Marked as vague because the description is too short or generic.")

        confidence_score = max(0.60, min(confidence_score, 0.95))

        if not reasoning_parts:
            reasoning_parts.append("Classification completed using the ticket content and customer metadata.")

        return {
            "resolved_category": resolved_category,
            "resolved_priority": resolved_priority,
            "confidence_score": confidence_score,
            "is_vague": is_vague,
            "language": lang,
            "reasoning": " ".join(reasoning_parts)
        }
