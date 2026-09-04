# Regenerates the auth + account-management artboards to match the shipped app
# (phone/E.164 + password + 6-digit OTP; no email/password or Google on sign-in).
# Run:  python _gen_auth_account.py     (from src/frontend/design)
import pathlib

LIGHT = "--green-800:#1B4332;--green-700:#2D6A4F;--green-600:#40916C;--green-100:#D8F3DC;--ink:#1A1C19;--ink-2:#5C5F5A;--ink-3:#8A8D87;--line:#E1E3DE;--fill:#EFF1EC;--bg:#F8F9FA;--surface:#FFFFFF;--danger:#B23B3B;"
DARK = "--green-800:#B7E4C7;--green-700:#40916C;--green-600:#52B788;--green-100:#17301F;--ink:#ECEFEA;--ink-2:#A8ADA4;--ink-3:#7C827A;--line:#2E362F;--fill:#242B25;--bg:#101511;--surface:#1A211C;--danger:#E39393;"
FI_LIGHT, FI_DARK = "#8A8D87", "#7C827A"

I = {
    "back": '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M15 6l-6 6 6 6"/></svg>',
    "phone": '<rect x="6" y="3" width="12" height="18" rx="2.5"/><path d="M10.5 18h3"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    "user": '<circle cx="12" cy="9" r="3.5"/><path d="M5 20c1.4-3.4 4-5 7-5s5.6 1.6 7 5"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M4 7l8 6 8-6"/>',
    "sms": '<path d="M4 5h16v11H8l-4 4Z"/><path d="M8 10h8"/><path d="M8 13h5"/>',
    "shield": '<path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6Z"/>',
    "trash": '<path d="M4 7h16"/><path d="M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/><path d="M6 7l1 12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-12"/>',
    "chev": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg>',
    "eye": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>',
}


def ficon(paths, stroke):
    return (f'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{stroke}" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{paths}</svg>')


def field(label, icon, text, hint, stroke, eye=False):
    cls = "ph" if hint else "val"
    eye_html = f'<span class="eye">{I["eye"]}</span>' if eye else ""
    return (f'<div class="field"><label>{label}</label>'
            f'<div class="input">{ficon(icon, stroke)}<span class="{cls}">{text}</span>{eye_html}</div></div>')


SHELL = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    :root{{{tokens}}}
    *{{box-sizing:border-box}}
    body{{margin:0;font-family:'Inter',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;color:var(--ink);background:var(--bg);-webkit-font-smoothing:antialiased}}
    a{{color:var(--green-700);text-decoration:none}}a:hover{{color:var(--green-800)}}
    .screen{{width:390px;background:var(--bg);display:flex;flex-direction:column;padding:16px 24px 28px;min-height:760px}}
    .rnd{{width:36px;height:36px;border-radius:11px;background:var(--surface);border:1px solid var(--line);display:flex;align-items:center;justify-content:center;color:var(--ink)}}
    .head{{margin:24px 0 20px}}
    .head .t{{font-size:26px;font-weight:700;letter-spacing:-.02em}}
    .head .s{{font-size:14px;color:var(--ink-2);margin-top:6px;line-height:1.55}}
    .form{{display:flex;flex-direction:column;gap:16px}}
    .field{{display:flex;flex-direction:column;gap:7px}}
    .field label{{font-size:12px;font-weight:600;color:var(--ink-2)}}
    .input{{height:48px;border-radius:12px;border:1px solid var(--line);background:var(--surface);display:flex;align-items:center;gap:10px;padding:0 13px;font-size:14px}}
    .input .val{{color:var(--ink)}}
    .input .ph{{color:var(--ink-3)}}
    .input .eye{{margin-left:auto;color:var(--ink-3)}}
    .forgot{{align-self:flex-end;font-size:12px;font-weight:600;margin-top:-4px}}
    .agree{{display:flex;gap:10px;align-items:flex-start;font-size:12px;color:var(--ink-2);line-height:1.5}}
    .cbox{{width:20px;height:20px;border-radius:6px;background:var(--green-700);display:flex;align-items:center;justify-content:center;color:#fff;flex:none}}
    .btn{{height:50px;border-radius:12px;font-size:15px;font-weight:600;display:flex;align-items:center;justify-content:center;border:1px solid transparent;background:var(--green-700);color:#fff;margin-top:2px}}
    .resend{{text-align:center;font-size:13px;font-weight:600;color:var(--green-700);margin-top:4px}}
    .foot{{margin-top:auto;text-align:center;font-size:13px;color:var(--ink-2);padding-top:22px}}
    .foot a{{font-weight:600}}
    .avatar{{width:64px;height:64px;border-radius:50%;background:var(--green-100);color:var(--green-800);display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:700;align-self:center;margin:6px 0 20px}}
    .glabel{{font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--ink-3);margin:18px 0 8px}}
    .grp{{background:var(--surface);border:1px solid var(--line);border-radius:14px;overflow:hidden}}
    .r{{display:flex;align-items:center;gap:12px;padding:14px 14px;border-top:1px solid var(--line);font-size:14px}}
    .grp .r:first-child{{border-top:none}}
    .r .ic{{color:var(--ink-2);display:flex}}
    .r .lb{{color:var(--ink)}}
    .r .vl{{margin-left:auto;color:var(--ink-3);font-size:13px}}
    .r .ch{{color:var(--ink-3);display:flex}}
    .r .vl + .ch{{margin-left:8px}}
    .r .lb + .ch{{margin-left:auto}}
    .r.danger .lb,.r.danger .ic{{color:var(--danger)}}
  </style>
</helmet>
<div class="screen">
  <span class="rnd">{back}</span>
  <div class="head"><div class="t">{title}</div>{sub}</div>
  {body}
</div>
</x-dc>
</body>
</html>
"""


def esc(s):
    return s.replace("&", "&amp;") if s else s


def render(fname, tokens, stroke, title, sub, body):
    sub_html = f'<div class="s">{esc(sub)}</div>' if sub else ""
    html = SHELL.format(tokens=tokens, back=I["back"], title=esc(title), sub=sub_html, body=body)
    pathlib.Path(fname).write_text(html, encoding="utf-8")


def form_screen(title, sub, fields, btn, *, forgot=None, terms=False, resend=False, foot=None):
    """Returns a body-builder taking (stroke) -> html."""
    def build(stroke):
        rows = []
        for f in fields:
            rows.append(field(f["label"], f["icon"], f["text"], f["hint"], stroke, f.get("eye", False)))
            if forgot and f is fields[-1] and not terms:
                rows.append(f'<a class="forgot" href="#">{forgot}</a>')
        if terms:
            rows.append(
                '<div class="agree"><span class="cbox"><svg width="13" height="13" viewBox="0 0 24 24" '
                'fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" '
                'stroke-linejoin="round"><path d="M5 12l4 4 10-10"/></svg></span><span>Tôi đồng ý với '
                '<a href="#">Điều khoản sử dụng</a> và <a href="#">Chính sách bảo mật</a>.</span></div>')
        rows.append(f'<button class="btn">{btn}</button>')
        if resend:
            rows.append(f'<div class="resend">{resend}</div>')
        html = '<div class="form">' + "".join(rows) + '</div>'
        if foot:
            html += f'<div class="foot">{foot}</div>'
        return html
    return title, sub, build


PW = dict(label="Mật khẩu", icon=I["lock"], text="••••••••", hint=True, eye=True)
NEWPW = dict(label="Mật khẩu mới", icon=I["lock"], text="Ít nhất 8 ký tự", hint=True, eye=True)
OTPF = dict(label="Mã xác thực", icon=I["sms"], text="000000", hint=True)
PHONE_IN = lambda lbl="Số điện thoại": dict(label=lbl, icon=I["phone"], text="0901 234 567", hint=True)

SCREENS = {
    "Login": form_screen(
        "Đăng nhập", "Tiếp tục quản lý tủ bếp của bạn",
        [PHONE_IN(), PW], "Đăng nhập", forgot="Quên mật khẩu?",
        foot='Chưa có tài khoản? <a href="#">Đăng ký</a>'),
    "Register": form_screen(
        "Tạo tài khoản", "Bắt đầu tiết kiệm thực phẩm cùng SweepFood",
        [dict(label="Họ và tên", icon=I["user"], text="Nguyễn Văn A", hint=True),
         PHONE_IN(),
         dict(label="Mật khẩu", icon=I["lock"], text="Ít nhất 8 ký tự", hint=True, eye=True)],
        "Tạo tài khoản", terms=True,
        foot='Đã có tài khoản? <a href="#">Đăng nhập</a>'),
    "Otp": form_screen(
        "Nhập mã xác thực", "Mã gồm 6 chữ số đã được gửi tới +84 901 234 567.",
        [OTPF], "Xác nhận", resend="Gửi lại mã"),
    "ForgotPassword": form_screen(
        "Quên mật khẩu", "Nhập số điện thoại tài khoản, chúng tôi sẽ gửi mã đặt lại mật khẩu.",
        [PHONE_IN()], "Gửi mã", resend="Quay lại đăng nhập"),
    "ResetPassword": form_screen(
        "Đặt lại mật khẩu", "Nhập mã đã gửi tới +84 901 234 567 và mật khẩu mới.",
        [OTPF, NEWPW], "Đặt lại mật khẩu", resend="Quay lại đăng nhập"),
    "EditProfile": form_screen(
        "Sửa hồ sơ", None,
        [dict(label="Họ và tên", icon=I["user"], text="Nguyễn Văn A", hint=False)], "Lưu"),
    "ChangePassword": form_screen(
        "Đổi mật khẩu", "Nhập mã xác thực và mật khẩu mới.",
        [OTPF, NEWPW], "Xác nhận", resend="Gửi lại mã"),
    "ChangeEmail": form_screen(
        "Đổi email", "Nhập email mới. Mã xác thực sẽ được gửi tới địa chỉ đó.",
        [dict(label="Email mới", icon=I["mail"], text="you@example.com", hint=True)], "Gửi mã"),
    "ChangePhone": form_screen(
        "Đổi số điện thoại", "Nhập số điện thoại mới. Mã xác thực sẽ được gửi tới số đó.",
        [PHONE_IN("Số điện thoại mới")], "Gửi mã"),
}


def profile_body(stroke):
    def row(icon, label, val=None, chev=True, danger=False):
        ic = ficon(icon, "currentColor")
        vl = f'<span class="vl">{val}</span>' if val else ""
        ch = ('<span class="ch"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" '
              'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
              '<path d="M9 6l6 6-6 6"/></svg></span>') if chev else ""
        d = " danger" if danger else ""
        return f'<div class="r{d}"><span class="ic">{ic}</span><span class="lb">{label}</span>{vl}{ch}</div>'
    return (
        '<div class="avatar">A</div>'
        '<div class="glabel">Thông tin</div>'
        '<div class="grp">'
        + row(I["user"], "Họ và tên", "Nguyễn Văn A")
        + row(I["mail"], "Email", "ban@email.com")
        + row(I["phone"], "Số điện thoại", "+84 901 234 567")
        + '</div>'
        '<div class="glabel">Bảo mật</div>'
        '<div class="grp">' + row(I["lock"], "Đổi mật khẩu") + '</div>'
        '<div class="glabel">&nbsp;</div>'
        '<div class="grp">' + row(I["trash"], "Xóa tài khoản", chev=False, danger=True) + '</div>'
    )


SCREENS["Profile"] = ("Hồ sơ & mật khẩu", None, profile_body)


def main():
    for name, (title, sub, build) in SCREENS.items():
        render(f"{name}.dc.html", LIGHT, FI_LIGHT, title, sub, build(FI_LIGHT))
        render(f"{name}Dark.dc.html", DARK, FI_DARK, title, sub, build(FI_DARK))
        print("wrote", name, "+ Dark")
    # QuotaReached is gone from the MVP (no gating).
    for f in ("QuotaReached.dc.html", "QuotaReachedDark.dc.html"):
        p = pathlib.Path(f)
        if p.exists():
            p.unlink()
            print("removed", f)


if __name__ == "__main__":
    main()
