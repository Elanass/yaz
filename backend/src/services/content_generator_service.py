class ContentGeneratorService:
    def generate_summary(self, patient):
        # Example logic to generate a structured summary
        return {
            "summary": f"Patient {patient.name} has a {patient.tumor_staging.stage} tumor. Treatment history includes {len(patient.treatment_history)} treatments.",
            "recommendations": ["Consider FLOT protocol", "Monitor perioperative risks"]
        }

    def generate_report(self, patient, format="PDF"):
        # Example logic to generate a report in the specified format
        summary = self.generate_summary(patient)
        if format == "PDF":
            return {"report": f"PDF Report: {summary['summary']}"}
        elif format == "HTML":
            return {"report": f"<html><body>{summary['summary']}</body></html>"}
        elif format == "Markdown":
            return {"report": f"# Report\n\n{summary['summary']}"}
        else:
            return {"error": "Unsupported format"}
