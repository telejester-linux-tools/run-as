# run-as

Launch a GUI application as a different local user, sharing the desktop owner's display and audio, with persistent per-user settings.

## Usage

```
run-as <target_user> <application>
```

**Examples:**

```bash
run-as hatingyou ptyxis
run-as collider firefox
run-as emacs gimp
```

A polkit authentication prompt appears once to authorise the `machinectl shell` session. The application launches in the background and the script exits.

## What it does

The script uses `machinectl shell` to open a session as the target user and launch the application with the following environment configured:

**Display** — Detects whether the caller is running Wayland or X11 and shares the appropriate socket. On Wayland, the Wayland socket is shared via ACL and `DISPLAY` is passed for XWayland fallback. On X11, `xhost` grants the target user access.

**Audio** — The target user's `PULSE_SERVER` is pointed at the desktop owner's PipeWire/PulseAudio socket (`$XDG_RUNTIME_DIR/pulse/native`). ACL permissions are granted on the socket so the connection is accepted. All launched users share the same audio devices and mixer as the desktop owner.

**D-Bus** — The target user's own D-Bus session bus is used (`/run/user/$UID/bus`), keeping their session services isolated from the desktop owner's.

**DConf/GTK settings** — The target user's DConf database (`~/.config/dconf/user`) is used for persistent settings, so each user's GTK application preferences are saved separately between runs.

**Session management** — If the target user has no active systemd user session, `loginctl enable-linger` is run on their behalf inside the session so that their session persists after the script exits.

**Chained invocations** — If `run-as` is invoked from within a session it previously created, `RUN_AS_OWNER_RUNDIR` (set by the outer invocation) ensures audio continues to route to the original desktop owner's PulseAudio socket rather than the intermediate user's.

## Requirements

### Hard requirements

| Requirement | Notes |
|---|---|
| systemd with `machinectl` | Provided by the `systemd-container` package on some distros |
| systemd-logind | Provides `loginctl`, `XDG_RUNTIME_DIR`, and `/run/user/$UID` |
| `setfacl` | From the `acl` package; filesystem must be mounted with ACL support |
| A running graphical session | `DISPLAY` or `WAYLAND_DISPLAY` must be set |

### Soft requirements

| Requirement | Effect if absent |
|---|---|
| PipeWire or PulseAudio | Audio sharing is silently skipped if `$XDG_RUNTIME_DIR/pulse/native` does not exist |
| `xhost` | Required for X11 display sharing; not needed on pure Wayland |
| DConf | Settings persistence has no effect outside GTK/GNOME applications |

## Distribution support

The script runs on any mainstream Linux distribution using systemd. It has been tested on **Fedora 43**.

It will work without modification on Ubuntu (20.04+), Debian (10+), Arch Linux, and openSUSE, provided the `acl` package is installed and the root filesystem is mounted with ACL support (the default on ext4, btrfs, and xfs on all of those distributions).

It will **not** work on non-systemd distributions such as Alpine Linux, Void Linux (runit), Devuan, or Gentoo with OpenRC, as `machinectl` and `loginctl` are systemd-specific tools with no equivalent.

### Fedora

`setfacl` is available in the `acl` package (`sudo dnf install acl`). ACL support is enabled by default on all standard Fedora filesystems.

`machinectl` is included in `systemd-container`, which is installed by default on Fedora Workstation.

## Bash completion

The file `run-as.bash-completion` provides tab completion: the first argument completes usernames and the second completes executable names from `$PATH`.

**Install for your user only:**

```bash
mkdir -p ~/.local/share/bash-completion/completions
cp run-as.bash-completion ~/.local/share/bash-completion/completions/run-as
```

**Install system-wide:**

```bash
sudo cp run-as.bash-completion /etc/bash_completion.d/run-as
```

Either location is picked up automatically by bash-completion without needing to source anything manually. Open a new shell after installing.

## Limitations

- ACL permissions granted to the target user are not automatically revoked when the application exits, as the cleanup function cannot run after backgrounding the launch. The permissions are scoped to runtime sockets and directories under `/run/user` which are cleaned up on logout or reboot.
- The target user's home directory is assumed to be `/home/$TARGET_USER`. Users with non-standard home directories will have DConf persistence silently misconfigured.
- The application name must be a valid executable name or path containing only alphanumeric characters, hyphens, underscores, dots, and slashes. Unvalidated input is passed to a shell string.
