import os
import re

api_dir = os.path.join(os.path.dirname(__file__), "..", "backend", "app", "api", "v1")
count_files = 0
count_replacements = 0

for filename in os.listdir(api_dir):
    if not filename.endswith(".py"):
        continue
    filepath = os.path.join(api_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    modified = False
    if 'context.tenant_id or "default-tenant"' in content:
        # Ensure get_enforced_tenant_id is imported
        if "from backend.app.core.tenant import" in content:
            if "get_enforced_tenant_id" not in content:
                content = re.sub(
                    r"(from backend\.app\.core\.tenant import [^\n]+)",
                    r"\1, get_enforced_tenant_id",
                    content
                )
                content = content.replace(", get_enforced_tenant_id, get_enforced_tenant_id", ", get_enforced_tenant_id")
        else:
            content = "from backend.app.core.tenant import get_enforced_tenant_id\n" + content

        occurrences = content.count('context.tenant_id or "default-tenant"')
        content = content.replace('context.tenant_id or "default-tenant"', 'get_enforced_tenant_id(context)')
        count_replacements += occurrences
        modified = True

    if modified:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        count_files += 1

print(f"Successfully processed {count_files} API router files with {count_replacements} tenant replacements.")
