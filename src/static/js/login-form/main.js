$(function () {
  "use strict";

  $(".form-control").on("input", function () {
    var $field = $(this).closest(".form-group");
    if (this.value) {
      $field.addClass("field--not-empty");
    } else {
      $field.removeClass("field--not-empty");
    }
  });
});

function convertFormToJSON(form) {
  console.log(form);
  return $(form)
    .serializeArray()
    .reduce(function (json, { name, value }) {
      json[name] = value;
      return json;
    }, {});
}

$("#login-form").submit((e) => {
  e.preventDefault();
  let dat = convertFormToJSON("#login-form");
  fetch("/login-student", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(dat),
  }).then((res) => {
    console.log(res);
    if (res.status == 401) {
      $(".message").addClass("message-danger");
      $(".message").html(`
        <div>
        Invalid ceredentials, try again.
        </div>
      `);
    }
    if (res.redirected) {
      location.href = res.url;
    }
  });
});
