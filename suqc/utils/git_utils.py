import os
import shutil
import subprocess
import platform


def jar_path(path: str, branch: str, commit_hash: str) -> str:
    jar_file_name = f"vadere-console_{branch}_{commit_hash}.jar"
    return os.path.join(path, jar_file_name)


def get_jar_file_from_vadere_repo(path: str, branch: str, commit_hash: str):
    # checkout commit and make a package
    # copy the generated jar-file to the user-defined path
    print(f"Branch: {branch}, commit hash: {commit_hash}")

    if platform.system() != "Linux":
        raise NotImplemented

    vadere = os.path.join(os.environ["CROWNET_HOME"],"vadere")
    vadere_jar_file = jar_path(path=path, branch=branch, commit_hash=commit_hash)
    vadere_commit = commit_hash
    if os.path.exists(vadere_jar_file) is False:

        return_code = subprocess.check_call(
            ["git", "-C", vadere, "pull", "origin", branch]
        )
        if vadere_commit:
            return_code = subprocess.check_call(
                ["git", "-C", vadere, "checkout", vadere_commit]
            )

        command = ["mvn", "clean", "-f", os.path.join(vadere, "pom.xml")]
        return_code = subprocess.check_call(command)
        command = [
            "mvn",
            "package",
            "-f",
            os.path.join(vadere, "pom.xml"),
            "-Dmaven.test.skip=true",
        ]
        return_code = subprocess.check_call(command)

        jar_file = os.path.join(vadere, "VadereSimulator/target/vadere-console.jar")

        shutil.copyfile(jar_file, vadere_jar_file)
