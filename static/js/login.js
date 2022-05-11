function sign_in() {
    let id = $("#input-username").val()               // id값을 읽어옴.
    let pw = $("#input-password").val()               // pw값을 읽어옴.

    if (id == "") {
        $("#help-id-login").text("아이디를 입력해주세요.")     // 아이디의 값들이 빈 값인지 아닌지 검사. -> ""(아이디 창이 비어 있으면) text를 보여줌.
        $("#input-username").focus()
        return;
    } else {
        $("#help-id-login").text("")
    }

    if (pw == "") {
        $("#help-password-login").text("비밀번호를 입력해주세요.")   // 비밀번호의 값들이 빈 값인지 아닌지 검사. -> ""(pw 창이 비어 있으면) text를 보여줌.
        $("#input-password").focus()
        return;
    } else {
        $("#help-password-login").text("")
    }
    $.ajax({
        type: "POST",
        url: "/login",
        data: {
            id_give: id,
            pw_give: pw
        },
        success: function (response) {
            if (response['result'] == 'success') {
                $.cookie('token', response['token'], {path: '/'});
                window.location.href = '/';

            } else {
                alert(response['msg'])
            }
        }
    });
}

$(document).ready(function () {
    $('#login_form').on("keypress", function (e) {
        if (e.keyCode === 13) {
            sign_in();
        }
    });
})



