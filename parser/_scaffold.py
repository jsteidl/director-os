import re
from datetime import date
from parser._core import save_log
from parser._files import get_log_file, get_prev_log_file


def scaffold_log(path):
    month_label = date.today().strftime("%B %Y")
    template = f"""# {month_label}

## Active To-Dos

### High-Priority

### Waiting On

### Resolved Dependencies

### Someday/Future

### Risks

### Accomplishments

### Wins Worth Mentioning

### Daily Log
"""
    path.write_text(template, encoding="utf-8")


def rollover_log():
    current = get_log_file()
    previous = get_prev_log_file()

    if not previous.exists():
        scaffold_log(current)
        return

    prev_content = previous.read_text(encoding="utf-8")

    task_match = re.search(r"### High-Priority(.*?)### Waiting On", prev_content, re.S)
    carried_tasks = ""
    if task_match:
        carried_tasks = "\n".join(
            line + " Carried:true" if not line.strip().endswith("Carried:true") else line
            for line in task_match.group(1).splitlines()
            if re.match(r"- \[ \]", line.strip())
        )

    dep_match = re.search(r"### Waiting On(.*?)### Resolved Dependencies", prev_content, re.S)
    carried_deps = ""
    if dep_match:
        carried_deps = "\n".join(
            line for line in dep_match.group(1).splitlines()
            if re.match(r"- .+ \| Owner:", line.strip())
        )

    someday_match = re.search(r"### Someday/Future(.*?)### Risks", prev_content, re.S)
    carried_someday = ""
    if someday_match:
        carried_someday = "\n".join(
            line for line in someday_match.group(1).splitlines()
            if re.match(r"- .+ \| Owner:", line.strip())
        )

    risk_match = re.search(r"### Risks(.*?)### Accomplishments", prev_content, re.S)
    carried_risks = ""
    if risk_match:
        carried_risks = "\n".join(
            line for line in risk_match.group(1).splitlines()
            if re.match(r"- .+ \| Owner:.+ \| Severity:", line.strip())
        )

    scaffold_log(current)
    content = current.read_text(encoding="utf-8")

    if carried_tasks:
        content = content.replace("### High-Priority\n", f"### High-Priority\n{carried_tasks}\n", 1)
    if carried_deps:
        content = content.replace("### Waiting On\n", f"### Waiting On\n{carried_deps}\n", 1)
    if carried_someday:
        content = content.replace("### Someday/Future\n", f"### Someday/Future\n{carried_someday}\n", 1)
    if carried_risks:
        content = content.replace("### Risks\n", f"### Risks\n{carried_risks}\n", 1)

    current.write_text(content, encoding="utf-8")
