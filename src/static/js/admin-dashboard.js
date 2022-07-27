let message = document.querySelector(".message")

document.querySelector("#display-table").addEventListener("click", (e) => {
    let target = e.target
    if (target.classList.contains("delete-user")) {
        let uuid = target.id
        if (uuid !== "") {
            fetch("/delete",{
                method : "POST",
                headers : {
                    "Content-Type" : "application/json"
                  },
                body : JSON.stringify({
                    uuid : uuid
                })
            }).then(res => {
                if (res.status == 500) {
                    message.innerHTML = `<div class="message-danger>Internal server error occured</div>`
                    return
                }
                if (res.status == 550) {
                    message.innerHTML = `<div class="message-danger>No such user exists in database</div>`
                    return
                }
                if (res.status == 400) {
                    message.innerHTML = `<div class="message-danger>Bad request, no user to provided</div>`
                    return
                }
                if (res.redirected) {
                    location.href = res.url
                }
            })
        }
    }
})