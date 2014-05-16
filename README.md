


# Getting Started

1. Pull code về
2. Chỉnh file deployment/development với IP server ảo được cấp
3. Chỉnh git để không commit các thay đổi trên file deployment/development

    ```bash
    $ git update-index --skip-worktree deployment/development
    ```

4. Deploy thử

    ```bash
    $ ssh-agent fish
    $ ssh-add /path/to/file/rdteam.pem

    $ ansible-playbook -i deployment/deployment deployment/analytics.yml -u clouduser
    ```

5. Chờ chạy xong, lên server kiểm tra lại

    ```bash
    $ ssh clouduser@<ip_server>

    # Xem list các process
    $ sudo supervisorctl

    Truy cập vào trình duyệt http://<your ip>/ để config giao diện
    ```
