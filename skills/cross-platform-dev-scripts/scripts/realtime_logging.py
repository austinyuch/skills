import subprocess
from pathlib import Path


def run_with_logging(cmd, log_file):
    log_file.parent.mkdir(parents=True, exist_ok=True)

    with open(log_file, "w", encoding="utf-8") as f:
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        if process.stdout:
            for line in process.stdout:
                print(line, end="")
                f.write(line)

        process.wait()

    return process.returncode


if __name__ == "__main__":
    log_file = Path("temp") / "test-output.log"
    returncode = run_with_logging("echo 'Test 1' && echo 'Test 2'", log_file)

    if returncode == 0:
        print(f"\n✅ 命令執行成功")
        print(f"📁 日誌檔案: {log_file}")
    else:
        print(f"\n❌ 命令失敗 (返回碼: {returncode})")
