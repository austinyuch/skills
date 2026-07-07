import sys
import subprocess


def run_command(cmd, check=True):
    try:
        result = subprocess.run(
            cmd, shell=True, check=check, capture_output=True, text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令執行失敗: {cmd}")
        print(f"錯誤碼: {e.returncode}")
        if e.stderr:
            print(f"錯誤訊息:\n{e.stderr}")
        sys.exit(e.returncode)


if __name__ == "__main__":
    result = run_command("echo 'Hello World'")
    print(result.stdout)

    result = run_command("docker --version", check=False)
    if result.returncode != 0:
        print("Docker 未安裝")
