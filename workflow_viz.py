MERMAID_HTML = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@9/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({ startOnLoad: true });
    </script>
</head>
<body style="background-color: transparent; margin: 0; padding: 0;">
    <div class="mermaid" style="display: flex; justify-content: center; font-family: sans-serif; height: 100vh;">
graph TD
    Start --> Step0[Step 0: Preprocessing]
    Step0 --> Step1[Step 1: Understanding]
    Step1 --> Step2[Step 2: Simplification]
    Step2 --> Step2A[Step 2A: Fairness Analysis]
    Step2A --> Step3[Step 3: Risk Analysis]
    Step3 --> Step4[Step 4: Risk Scoring]
    Step4 --> Step5[Step 5: Decision Agent]
    Step5 --> Step6[Step 6: Advisory Agent]
    Step6 --> Step7[Step 7: Q&A Agent]
    
    style Step2A fill:#ffcc00,stroke:#333
    style Step4 fill:#ff4b4b,stroke:#333
    </div>
</body>
</html>
"""
