#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=/opt/fieldos/installer/provisioning

install -D -m 0644 "$ROOT/assets/fieldos-wallpaper.svg" \
  /usr/share/backgrounds/fieldos/fieldos-wallpaper.svg
install -D -m 0644 "$ROOT/assets/fieldos.svg" \
  /usr/share/icons/hicolor/scalable/apps/fieldos.svg
install -D -m 0644 "$ROOT/fieldos.desktop" \
  /usr/share/applications/fieldos-nomad.desktop
install -D -m 0644 "$ROOT/fieldos-start-here.desktop" \
  /usr/share/applications/fieldos-start-here.desktop
install -D -m 0644 "$ROOT/fieldos-sources.desktop" \
  /usr/share/applications/fieldos-sources.desktop
install -D -m 0644 "$ROOT/fieldos-start-here.html" \
  /usr/share/doc/fieldos/START-HERE.html

# System defaults apply to new users; existing per-user preferences win.
profile=/etc/dconf/profile/user
install -d -m 0755 /etc/dconf/profile /etc/dconf/db/local.d
if [[ ! -e "$profile" ]]; then
  printf 'user-db:user\nsystem-db:local\n' > "$profile"
elif ! grep -qxF 'system-db:local' "$profile"; then
  printf '\nsystem-db:local\n' >> "$profile"
fi
cat > /etc/dconf/db/local.d/00-fieldos <<'EOF'
[org/gnome/desktop/background]
picture-uri='file:///usr/share/backgrounds/fieldos/fieldos-wallpaper.svg'
picture-uri-dark='file:///usr/share/backgrounds/fieldos/fieldos-wallpaper.svg'
picture-options='zoom'

[org/gnome/desktop/interface]
color-scheme='prefer-dark'

[org/gnome/shell]
favorite-apps=['firefox_firefox.desktop', 'org.gnome.Nautilus.desktop', 'fieldos-start-here.desktop', 'fieldos-nomad.desktop']
EOF
dconf update
if command -v update-desktop-database >/dev/null; then
  update-desktop-database /usr/share/applications
fi
if command -v gtk-update-icon-cache >/dev/null; then
  gtk-update-icon-cache -f /usr/share/icons/hicolor
fi
