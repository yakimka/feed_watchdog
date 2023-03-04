import shutil

if __name__ == "__main__":
    # copy files from /app/frontend to /var/www/frontend
    shutil.copytree(
        "/app/frontend",
        "/var/www/frontend",
        dirs_exist_ok=True,
    )
