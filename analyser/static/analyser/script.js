function onFirmTopicHeatmapButtonClicked() {
    $.get("/analyser/get_firm_heatmap", function(data) {
        document.getElementById("image_place").innerHTML = data
    });
    
}

function onFirmTopicDistributionButtonClicked() {

}

function onComplementarityHeatmapButtonClicked() {
    // $.get("/analyser/get_complementarity_heatmap", function(data) {
    //     document.getElementsByClassName("image_place")[0].innerHTML = data
    // });
    $.getJSON("/analyser/get_complementarity_heatmap", function(heatmap) {
        $.getJSON("/analyser/get_firm_list", function(firms) { 
            var data = [
                {
                  z: heatmap,
                  x: firms,
                  y: firms,
                  type: 'heatmap'
                }
              ];
            var layout = {
            //autosize: true,
            width: 700,
            height: 700,
            xaxis : {
                visible:false,
                showticklabels:false
            },
            yaxis : {
                visible:false,
                showticklabels:false
            },
        }
            var config = {
                // responsive: true
            }
              
            Plotly.newPlot('image_place', data, layout, config);
        })});

}

function onMostComplementaryFirmsButtonClicked() {
    var sel = document.getElementById("input_firm_name");
    if (sel)
    {
        var firm= sel.options[sel.selectedIndex].text;
        $.get("/analyser/get_complementary_firms", {"firm":firm}, function(data) {
            document.getElementById("image_place").innerHTML = data
        });
    }
    else
    {
        alert("Необходимо сначала построить матрицу взаимодополняемости")
    }
}

function onResetButtonClicked() {

    $.get("/analyser/reset", function(result) {updateStatusBar()})
}

function onAnalyseButtonClicked() {
    $.get("/analyser/get_status", function(result) {
        var status;
        if (result == "ready to start")
        {
            startAnalysing()
        }
        else if (result.slice(0,4) == "done")
        {

            startAnalysing()
        }
        else if (result == "working")
            alert("Анализатор уже работает")
        else if (result == "not ready")
            alert("Анализатор не готов к запуску; необходимо сначала кластеризовать патенты")
        else
            alert("Неизвестная ошибка")
    });
}

function startAnalysing() {
    var threshold = document.getElementsByClassName("input_patent_threshold")[0].value
    status_bar.value = "Анализатор работает"
    $.get("/analyser/start_analyse", {"threshold":threshold}, function(result) {updateStatusBar()})
}

function updateStatusBar() {
    $.get("/analyser/get_status", function(result) {
        var status;
        if (result == "working")
            status = "Анализатор работает"
        else if (result.slice(0,4) == "done")
        {
            status = "Готово, проанализировано" +  result.slice(4) + " предприятий"
            //status = "Done, analysed " +  result.slice(4) + " firms"
            updateFirmList()
        }
        else if (result == "ready to start")
            status = "Готов к запуску анализа"
        else if (result == "not ready")
            status = "Не готов к запуску; необходимо сначала кластеризовать патенты"
        else
            status = "Неизвестный статус"
        status_bar.value = status
    });
}

function updateFirmList() {
    $.get("/analyser/get_firm_choosing_list", function(data) {
        document.getElementById("input_firm_name_div").innerHTML = data
    });
}

$(function() {
    status_bar = document.getElementsByClassName("status_string")[0]
    updateStatusBar()
    lastFirm = 2
})

