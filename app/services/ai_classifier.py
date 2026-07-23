import pickle
import os


class AIClassifierService:
    """
    AI-based department classifier for incoming complaints.

    How it works:
    - If a trained sklearn model (complaint_classifier.pkl) exists and loads correctly,
      it uses that to predict the department ID from complaint text.
    - If no model is trained yet, it falls back to a keyword-based rule engine
      that maps common keywords to department IDs, so the app still works out-of-the-box.

    To train the real model, collect complaint samples and run the training script.
    """

    KEYWORD_RULES = {
        1: ["road", "pothole", "street", "highway", "bridge", "traffic", "signal", "footpath"],
        2: ["water", "pipe", "drainage", "sewage", "flood", "leak", "supply"],
        3: ["electricity", "power", "electric", "light", "transformer", "outage", "wire"],
        4: ["garbage", "waste", "sanitation", "cleanliness", "dust", "bin", "trash"],
        5: ["hospital", "health", "medical", "doctor", "ambulance", "medicine", "clinic"],
        6: ["school", "education", "teacher", "college", "student", "exam", "library"],
        7: ["police", "crime", "safety", "security", "theft", "assault", "harassment"],
        8: ["tax", "revenue", "property", "certificate", "license", "permit", "fine"],
    }

    def __init__(self, model_path: str = "app/ai_models/complaint_classifier.pkl"):
        self.model_path = model_path
        self.model = self._load_model()

    def _load_model(self):
        """Try to load a trained sklearn model. Return None if unavailable or corrupt."""
        if not os.path.exists(self.model_path):
            return None
        try:
            with open(self.model_path, "rb") as f:
                model = pickle.load(f)
            print("[AI] Classifier model loaded successfully.")
            return model
        except Exception as e:
            print(f"[AI] Could not load model ({e}). Falling back to keyword rules.")
            return None

    def predict_department(self, text: str) -> int | None:
        """
        Predict the department ID for a given complaint text.
        Uses trained ML model if available, else falls back to keyword matching.
        Returns a department ID (int) or None if no match found.
        """
        if not text:
            return None

        # Try ML model first
        if self.model is not None:
            try:
                prediction = self.model.predict([text])
                return int(prediction[0])
            except Exception as e:
                print(f"[AI] Model prediction error: {e}. Using keyword fallback.")

        # Keyword fallback
        return self._keyword_match(text.lower())

    def _keyword_match(self, text: str) -> int | None:
        """
        Simple keyword-based department routing.
        Returns the department_id with the most keyword hits, or None.
        """
        scores = {}
        for dept_id, keywords in self.KEYWORD_RULES.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[dept_id] = score

        if not scores:
            return None
        return max(scores, key=scores.get)


# Singleton instance — imported by routers
ai_classifier = AIClassifierService()