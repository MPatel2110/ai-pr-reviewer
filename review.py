from dotenv import load_dotenv
from providers.gemini import GeminiProvider


# verify the LLM returns multiple comments correctly.
HARDCODED_DIFF = """
diff --git a/calculator.py b/calculator.py
index 0000000..1111111 100644
--- a/calculator.py
+++ b/calculator.py
@@ -0,0 +1,8 @@
+def divide(a, b):
+    result = a / b
+    return result
+
+def get_user_password(username):
+    query = "SELECT password FROM users WHERE name = '" + username + "'"
+    return execute_query(query)
+
"""


def main():
    load_dotenv()
    provider = GeminiProvider()
    
    print("Sending diff to Gemini...\n")
    comments = provider.review_diff(HARDCODED_DIFF)
    
    if not comments:
        print("No issues found.")
        return
    
    print("=" * 60)
    print(f"REVIEW — {len(comments)} comment(s)")
    print("=" * 60)
    
    for i, comment in enumerate(comments, 1):
        print(f"\n[{i}] {comment.severity.value.upper()} · {comment.category.value}")
        print(f"    {comment.file}:{comment.line}")
        print(f"    {comment.comment}")


if __name__ == "__main__":
    main()