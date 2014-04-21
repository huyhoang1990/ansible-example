


Lệnh ansible để khởi động tất cả là :
    ansible-playbook -i deployment/deployment deployment/analytics.yml -u clouduser

Lênh để xem supervisord ( chưa set được thành global )
    sudo supervisorctl -c /etc/supervisor/supervisord.conf
