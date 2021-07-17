

function onClustererButtonClicked() {
    $.get("/clusterer/get_status", function(result) {
        if (result == "working")
            alert("Кластеризатор уже работает, подождите")
        else if (result.slice(0,4) == "done")
        {
            startClustering()
        }
        else if (result == "ready to start")
        {
            startClustering()
        }
        else if (result == "not ready")
        {
            alert("Необходимо сначала распарсить патенты")
        }
    });
}



function startClustering() {
    var alpha = document.getElementsByClassName("input_alpha")[0].value
    var gamma = document.getElementsByClassName("input_gamma")[0].value
    var eta = document.getElementsByClassName("input_eta")[0].value
    var n = document.getElementsByClassName("input_n")[0].value
    var L = document.getElementsByClassName("input_L")[0].value
    var filter_str = document.getElementsByClassName("input_filter")[0].value
    status_bar.value = "Кластеризатор работает"
    $.get("/clusterer/start_clustering", {"alpha":alpha, "gamma":gamma, "eta":eta, "n":n, "L":L, "filter_str":filter_str}, onClusteringEnd);
}

function updateStatusBar() {
    $.get("/clusterer/get_status", function(result) {
        var status;
        if (result == "working")
            status = "Кластеризатор работает"
        else if (result.slice(0,4) == "done")
            status = "Готово, кластеризовано" +  result.slice(4) + " патентов"
        else if (result == "ready to start")
            status = "Готов к запуску"
        else if (result == "not ready")
            status = "Не готов к запуску; необходимо сначала распарсить патенты"
        else
            status = "Неизвестный статус"
        status_bar.value = status
    });
}

function onClusteringEnd(data) {
    updateStatusBar()
    //status_bar.value = "Готово, распарсено " + data + " файлов"
}

function onResetButtonClicked() {

    $.get("/clusterer/reset", function(result) {updateStatusBar()})
}

$(function() {
    status_bar = document.getElementsByClassName("status_string")[0]
    updateStatusBar()
})

