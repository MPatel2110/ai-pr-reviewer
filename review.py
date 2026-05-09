from dotenv import load_dotenv
from providers.gemini import GeminiProvider

HARDCODED_DIFF = """
diff --git a/calculator.py b/calculator.py
index 0000000..1111111 100644
--- a/calculator.py
+++ b/calculator.py
@@ -0,0 +1,5 @@
+def divide(a, b):
+    \"\"\"Divide a by b and return the result.\"\"\"
+    result = a / b
+    return result
+
"""


def main():

    load_dotenv()
    provider = GeminiProvider()

    print("Sending diff to Gemini...\n")
    review = provider.review_diff(HARDCODED_DIFF)

    print("=" * 60)
    print("REVIEW")
    print("=" * 60)
    print(review)
    
if __name__ == "__main__":
    main()