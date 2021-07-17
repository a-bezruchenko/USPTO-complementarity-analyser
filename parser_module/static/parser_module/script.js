

function onParseButtonClicked() {
    $.get("/parser/get_status", function(result) {
        if (result == "working")
            alert("Патенты уже парсятся, подождите")
        else if (result.slice(0,4) == "done")
        {
            startParsing()
        }
        else if (result == "ready to start")
        {
            startParsing()
        }
    });
}

function onResetButtonClicked() {

    $.get("/parser/reset", function(result) {updateStatusBar()})
}

function startParsing() {
    var input_directory = document.getElementsByClassName("input_dirname")[0].value
    status_bar.value = "Парсер работает"
    $.get("/parser/start_parsing", { input_dir: input_directory}, onParsingEnd);
}

function updateStatusBar() {
    $.get("/parser/get_status", function(result) {
        var status;
        if (result == "working")
            status = "Парсер работает"
        else if (result.slice(0,4) == "done")
            status = "Готово, распарсено" +  result.slice(4) + " файлов"
        else if (result == "ready to start")
            status = "Готов к запуску"
        else 
            status = "Неизвестный статус"
        status_bar.value = status
    });
}

function onParsingEnd(data) {
    updateStatusBar()
    //status_bar.value = "Готово, распарсено " + data + " файлов"
}

$(function() {
    status_bar = document.getElementsByClassName("status_string")[0]
    updateStatusBar()
})

