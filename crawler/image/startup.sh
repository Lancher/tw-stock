#!/bin/bash

mkdir -p /var/run/sshd

# lxde
chown -R root:root /root
mkdir -p /root/.config/pcmanfm/LXDE/
cp /usr/share/doro-lxde-wallpapers/desktop-items-0.conf /root/.config/pcmanfm/LXDE/

# vnc
if [ -n "$VNC_PASSWORD" ]; then
    echo -n "$VNC_PASSWORD" > /.password1
    x11vnc -storepasswd $(cat /.password1) /.password2
    chmod 400 /.password*
    sed -i 's/^command=x11vnc.*/& -rfbauth \/.password2/' /etc/supervisor/conf.d/supervisord.conf
    export VNC_PASSWORD=
fi

# syslog & cron log
rsyslogd
cron -L15

# Sendgrid mail service
sed -i "s/^relayhost.*/relayhost = [smtp.sendgrid.net]:2525/g" /etc/postfix/main.cf
cat << EOF >> /etc/postfix/main.cf

smtp_tls_security_level = encrypt
smtp_sasl_auth_enable = yes
smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd
header_size_limit = 4096000
smtp_sasl_security_options = noanonymous
EOF
echo "[smtp.sendgrid.net]:2525 steve.liushihao:@sendgrid444555666d" > /etc/postfix/sasl_passwd
postmap /etc/postfix/sasl_passwd
rm /etc/postfix/sasl_passwd
chmod 600 /etc/postfix/sasl_passwd.db
/etc/init.d/postfix start

# web & nginx & supervisor
cd /usr/lib/web && ./run.py > /var/log/web.log 2>&1 &
nginx -c /etc/nginx/nginx.conf
exec /bin/tini -- /usr/bin/supervisord -n
