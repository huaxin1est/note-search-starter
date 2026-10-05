from fastapi.testclient import TestClient
from api import app

test_examples = {
    "地址修正": [("csapp-linking-practice.md", 4)],
    "如何读取中文文件": [("python.txt", 2)],
    "HTTP 请求成功的状态码": [
        ("http.md", 4),
        (r"topics\api-request-flow.md", 5),
    ],
    "静态库和共享库有什么差别": [("csapp-linking-practice.md", 5)],
    "找不到函数定义报什么错": [("csapp-linking-practice.md", 6)],
}

client = TestClient(app)
test_sum = len(test_examples)
pass_test = 0

for number, (query, expected_answers) in enumerate(test_examples.items(), start=1):
    response = client.get("/hybrid-search", params={"query": query})
    data = response.json()
    results = data.get("results", [])

    if response.status_code != 200 or not results:
        print(f"Test {number}: 不通过，没有获得有效结果")
        continue

    first_result = results[0]
    actual = (first_result["file"], first_result["paragraph"])

    if actual in expected_answers:
        print(f"Test {number}: 通过｜{query}")
        pass_test += 1
    else:
        expected_text = " 或 ".join(
            f"{file} 第 {paragraph} 段"
            for file, paragraph in expected_answers
        )
        print(f"Test {number}: 不通过｜{query}")
        print(f"  预期：{expected_text}")
        print(f"  实际：{actual[0]} 第 {actual[1]} 段")

pass_rate = pass_test / test_sum if test_sum else 0
print(f"Top-1 命中率：{pass_test}/{test_sum}（{pass_rate:.0%}）")
