import requests
import json
from bs4 import BeautifulSoup

config = json.load(open("config.json"))
allowedAssignments = ["Video", "Example"]
headers = {
    "cookie": f"sessionid={config['session_id']}; csrftoken={config['csrf_token']}",
}

coursePage = requests.get(
    f"https://codehs.com/student/{config['student_id']}/section/{config['course_id']}/assignments", headers=headers).text
courseSoup = BeautifulSoup(coursePage)
for assignment in courseSoup.find("div", {"id": "search-items"}).findChildren(recursive=False):
    try:
        assignmentType = allowedAssignments[allowedAssignments.index(assignment.find("span", {"class": "badge"}).text)]
    except ValueError:
        continue
    assignmentURL = f"https://codehs.com{assignment.attrs.get('href')}"
    assignmentText = requests.get(assignmentURL, headers=headers).text
    # don't care enough to optimize lol
    if assignmentType == "Example":
        assignmentIdIndex = assignmentText.find("studentAssignmentID: ")
        assignmentId = assignmentText[assignmentIdIndex + 21:assignmentText.find(",", assignmentIdIndex)]
    elif assignmentType == "Video":
        assignmentIdIndex = assignmentText.find("studentAssignmentID\": ")
        assignmentId = assignmentText[assignmentIdIndex + 21:assignmentText.find(",", assignmentIdIndex)]
    print(requests.post("https://codehs.com/lms/ajax/submit_assignment", headers=dict({
        "x-csrftoken": config["csrf_token"],
        "referer": assignmentURL
    }, **headers), data={
        "student_assignment_id": assignmentId,
        "method": "submit_assignment"
    }).text)
# for module in courseSoup.find("div", {"id": "course-sec"}).findChildren(recursive=False):
#     print(module.find("div", {"class": "wrap"}).find("div", {"class": "lessons-sec"}).find("div").attrs.get("class"))
