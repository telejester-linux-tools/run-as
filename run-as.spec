Name:           run-as
Version:        1.0.0
Release:        1%{?dist}
Summary:        Launch GUI applications as a different local user

License:        GPL-3.0-or-later
URL:            https://github.com/telejester-linux-tools/run-as
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

Requires:       bash
Requires:       systemd
Requires:       acl
Requires:       xorg-x11-server-utils

%description
run-as launches a GUI application as a different local user on the same
machine, sharing the desktop owner's display and PipeWire/PulseAudio
audio session via ACL permissions. Each user gets their own D-Bus session
and persistent DConf settings. Uses machinectl shell for session creation.

%prep
%autosetup

%build
# nothing to build

%install
install -Dm755 run-as %{buildroot}%{_bindir}/run-as
install -Dm644 run-as.bash-completion \
    %{buildroot}%{_datadir}/bash-completion/completions/run-as

%files
%license LICENSE
%doc README.md
%{_bindir}/run-as
%{_datadir}/bash-completion/completions/run-as

%changelog
* Fri Apr 24 2026 Jason <jason@shadowy.org> - 1.0.0-1
- Initial release
