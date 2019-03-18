Dropzone.autoDiscover = false;

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

window.onload = function(){
    $('#transfusion_dropzone').dropzone({
        dictDefaultMessage: 'Drop transfusion file (or click)',
        url: '/utilization/file_upload/',
        thumbnailWidth  : '50',
        thumbnailHeight : '50',
        headers: {'X-CSRFToken': getCookie('csrftoken')},
        accept: function(file, done){
            var lower_name = file.name.toLowerCase();
            if (!lower_name.includes('deidentified')) {
                alert('The file name must contain the word "deidentified" and cannot contain sensitive information.')
            } else {
                done();
            }
        },
        success: function(file, data){
            var specialty_select = document.getElementById('specialty_box');
            var option = document.createElement('option');
            option.text = '';
            option.value = '';
            specialty_select.add(option);
            data.specialties.forEach(function(specialty){
                var option = document.createElement('option');
                option.text = specialty;
                option.value = specialty;
                specialty_select.add(option);
            })

            var location_select = document.getElementById('location_box');
            var option = document.createElement('option');
            option.text = '';
            option.value = '';
            location_select.add(option);
            data.locations.forEach(function(location){
                var option = document.createElement('option');
                option.text = location;
                option.value = location;
                location_select.add(option);
            })
//            $(file.previewElement).fadeOut(2000);
        },
        complete: function(file){

        },
    })
}

function add_graphics(){
    var products = document.getElementById("product_box").value,
        location = document.getElementById("location_box").value,
        specialty = document.getElementById("specialty_box").value,
        per_day = document.getElementById("per_day_box").value,
        start_date = document.getElementById("start_date_box").value,
        end_date = document.getElementById("end_date_box").value;

    var criteria = {"products":products, "location":location, "specialty":specialty, "per_day":per_day,
                    "start_date":start_date, "end_date":end_date};

    $.getJSON("/utilization/utilization_data/", criteria, function(utilization_data) {
        var data = utilization_data;
        $(".new-div").remove();
        console.log(data);
        if (data['PLATELETS'].units.length>0){add_swarm(data['PLATELETS'], "platelets")};
        if (data['RED CELLS'].units.length>0){add_swarm(data['RED CELLS'], "RBCs")};
        if (data['PLASMA'].units.length>0){add_swarm(data['PLASMA'], "plasma")};
        if (data['CRYOPPT'].units.length>0){add_swarm(data['CRYOPPT'], "cryo")};
    });
}

function add_swarm(data, product){
    if (product=="platelets"){
        var bin_values = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 1000];
        var x_text = "Most recent platelet count";
    }

    if (product=="RBCs"){
        var bin_values = [0, 4, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13,
                          13.5, 14, 14.5, 15, 20];
         var x_text = "Most recent hemoglobin";
    }

    if (product=="plasma"){
        var bin_values = [0, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 28, 30, 32,
                          34, 36, 40, 44, 60, 80, 100];
        var x_text = "Most recent prothrombin time";
    }

    if (product=="cryo"){
        var bin_values = [0, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 300, 350, 400, 450, 500];
         var x_text = "Most recent fibrinogen";
    }

    var new_div = d3.select("#svg-div")
        .append("div")
        .attr("class", "new-div")
    var margin = {top:10, right:30, bottom:45, left:40};
    var width = 0.9*$('#svg-div').width();
    var height = 500 - margin.top - margin.bottom;

    var x = d3.scaleBand()
        .rangeRound([margin.left+44.5, width-80])
        .domain(bin_values);

    var x_visual = d3.scaleBand()
        .rangeRound([0, width])
        .domain(bin_values);

    var xAxis = d3.axisBottom(x_visual);

    var select_lines = 0;
    var select_vals = [];

    var svg = new_div.append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .on("click", function(){
            var tick_spacing = x_visual(bins[1].x1)-x_visual(bins[1].x0);

            if (select_lines < 2){
                var coords = d3.mouse(this);
                var x_coord = coords[0];

                // Find the closest bin value
                var current = bin_values[0];
                var position = 0;
                for(var i = 0; i < bin_values.length; i ++){
                    if (Math.abs(x_coord - x_visual(bin_values[i])) < Math.abs(x_coord - x_visual(current))){
                        current = bin_values[i];
                        position = i;
                    }
                }

                if (current == bin_values[bin_values.length-1] && (x_coord-x_visual(current)>(tick_spacing/2))){
                    x_coord = x_visual(current)+tick_spacing;
                    select_vals.push(current);
                }
                else{
                    x_coord = x_visual(current);
                    select_vals.push(bin_values[position-1]);
                }

                console.log(select_vals);

                g.append("line")
                    .attr("x1", x_coord)
                    .attr("x2", x_coord)
                    .attr("y1", 0)
                    .attr("y2", height)
                    .attr("class", "select_line")
                    .attr("stroke-width", 2)
                    .attr("stroke", "rgba(212,43,0, 1)")
                    .attr("transform", function(){
                            return "translate(-"+tick_spacing/2+",0)";
                        })
                    .style("stroke-dasharray", [5,2]);
                select_lines++;


                if (select_lines == 2){
                    if (select_vals[0]<select_vals[1]){
                        var min = select_vals[0];
                        var max = select_vals[1];
                    }
                    else{
                        var min = select_vals[1];
                        var max = select_vals[0];
                    }
                    var selected_units = [];
                    data.units.forEach(function(unit){
                        if (unit.value >= min && unit.value <=max){
                            selected_units.push(unit);
                        }
                    })
                    var save_button = statistics_g.append("svg:rect")
                            .attr("y", stat_start + 65)
                            .attr("x", -5)
                            .attr("height", 20)
                            .attr("width", 250)
                            .attr("id", "save_button")
                            .style("fill", "rgba(212,43,0, 1)");

                    var save_text = statistics_g.append("text")
                        .attr("y", stat_start + 80)
                        .attr("x", 122.5)
                        .style("fill", "white")
                        .text("Save")
                        .attr("id", "save_text")
                        .style("text-anchor", "middle");

                    $('#save_button').on('click', function(){save_selection(select_vals, data);});
                    $('#save_text').on('click', function(){save_selection(select_vals, data);});

                    statistics("selected", "Selected transfusions", selected_units, stat_start, statistics_g);
                }
            }
            else if (select_lines>=2){
                g.selectAll("line.select_line").remove();
                select_lines=0;
                select_vals = [];
                d3.select("#save_button").remove()
                d3.select("#save_text").remove();
                d3.select("#selected").remove();
            }
        })

    var x_label = svg.append("text")
        .attr("y", height+margin.top+35)
        .attr("x", (width-margin.left-margin.right)/2)
        .attr("dominant-baseline", "baseline")
        .text(x_text);

    var g = svg.append("g")
        .attr("transform", "translate("+margin.left+","+margin.top+")");

    var statistics_g = svg.append("g")
        .attr("transform", "translate("+(width-250)+","+(margin.top+15)+")");

    statistics_g.append("text")
        .attr("x", 125)
        .attr("text-anchor", "middle")
        .text("Statistics")
        .style("font-weight", "bold");

    var stat_start = statistics("all", "All transfusions", data.units, 25, statistics_g);

    var histogram = d3.histogram()
        .value(function(d){return d.value;})
        .thresholds(bin_values);

    var bins = histogram(data.units);

    var list_length = d3.max(bins, function(d){
        return d.length;
        });

    g.append("g")
        .attr("class", "axis axis--x")
        .attr("transform", "translate(0,"+height+")")
        .call(xAxis);

    if ((list_length/5)*6.5+4>height){
        draw_histogram(data, bins, margin, height, width, list_length, bin_values, g, x, x_visual);
    } else{
        draw_dot_chart(bins, margin, height, width, list_length, bin_values, g, x, x_visual);
    };
}

function draw_dot_chart(bins, margin, height, width, list_length, bin_values, g, x, x_visual){
    // The y axis domain must be adjusted because the max number of circles/transfusions
    // in a bin won't necessarily be at max height
    var domain_factor = list_length*(height+margin.top)/(4+6.5*(list_length/5));

    var y = d3.scaleLinear()
        .range([height+margin.top, margin.top])
        .domain([0,domain_factor]);

    var tick_spacing = x(bins[1].x1)-x(bins[1].x0);
    var circles_amount = Math.floor((tick_spacing-2)/6.5);

    // The x1 value of the last bin needs to be set to one of the bin_values
    // or it will not scale properly on the x domain
    bins[bins.length-1].x1 = bin_values[bin_values.length-1];
    bins[0].x0 = bin_values[0];

    var circleG = g.selectAll(".circle")
        .data(bins)
        .enter()
        .append("g")
            .attr("class", "circle-g")
            .attr("transform", function(d, i){
                return "translate("+(x_visual(d.x1)-14.5)+","+height+")"
                }
             );
    var tip = d3.tip()
        .attr('class', 'd3-tip')
        .offset([-10, 0])
        .html(function(d) {
        return "<strong>"+d.test+"</strong> <span style='color:rgba(212,43,0, 1)'>" + d.value + "</span><br> \
                <strong>Specialty:</strong> <span style='color:rgba(212,43,0, 1)'>" + d.specialty + "</span><br>\
                <strong>Location:</strong> <span style='color:rgba(212,43,0, 1)'>" + d.location+ "</span>";
    })

    g.call(tip);

    var circles = circleG.selectAll("circle")
        .data(d=>d.map((p, i)=>{
                return{
                idx:i,
                value:p.value,
                color:p.color,
                specialty:p.specialty,
                test:p.test,
                location:p.location,
        }}) )
        .enter()
        .append("circle")
        .attr("cx", function (d) {return 6.5*(d.idx%5);})
        .attr("cy", function (d) {return 2+6.5*(-Math.ceil((1+d.idx)/5))})
        .attr("r", 3)
        .attr("class", "transfusion")
        .attr("data-value", function(d){return d.value})
        .style("fill", function(d) { return d.color; })
        .on('mouseover', function(d){
            d3.select(this).style('fill', 'rgba(212,43,0, 1');
            tip.show(d);
        })
        .on('mouseout', function(d){
            d3.select(this).style('fill', d.color);
            tip.hide(d);
        });

    g.append("g")
        .call(d3.axisLeft(y))
        .attr("transform", "translate(0,-10)");
}

function draw_histogram(data, bins, margin, height, width, list_length, bin_values, g, x, x_visual){
    console.log("draw a histogram");
    var y = d3.scaleLinear()
        .range([height, 0])
        .domain([0, d3.max(bins, function(d){return d.length;})]);

    bins[bins.length-1].x1 = bin_values[bin_values.length-1];
    bins[0].x0 = bin_values[0];

    var tick_spacing = x_visual(bins[1].x1)-x_visual(bins[1].x0);

    console.log(bins);
    var bar = g.selectAll(".bar")
        .data(bins)
        .enter().append("g")
        .attr("class", "bar")
        .attr("transform", function(d, i){return "translate("+x_visual(d.x0)+","+y(d.length)+")"});

    bar.append("rect")
        .attr("x", 1)
        .attr("width", x_visual(bins[1].x1)-x_visual(bins[1].x0)-10)
        .attr("height", function(d){return height - y(d.length)})
        .style("fill", "rgba(0, 0, 0, 1")
        .attr("transform", function(d){
            return "translate("+(5+tick_spacing/2)+",0)";
         });

    g.append("g")
        .call(d3.axisLeft(y))
        .attr("transform", "translate(0,0)");
}

function save_selection(select_vals, data){
    if (select_vals[0]<select_vals[1]){
        var min = select_vals[0];
        var max = select_vals[1];
    }
    else{
        var min = select_vals[1];
        var max = select_vals[0];
    }

    var selected_transfusions = "";
    data.units.forEach(function(transfusion){
        if(transfusion.value>=min && transfusion.value<=max){
            selected_transfusions += transfusion.line+"\r\n";
        }
    });

    var blob = new Blob([selected_transfusions], {type: "text/plain;charset=utf-8"});
    saveAs(blob, "Selected Transfusions.txt", true);
}

function statistics(id, label, transfusions, statistics_y, statistics_g){
    var statistics_content = statistics_g.append("g")
        .attr("id", id)

    var statistics_box = statistics_content.append("rect")
        .attr("y", statistics_y-12)
        .attr("x", -5)
        .style("fill", "rgba(255, 255, 255, 1)")
        .attr("height", 45)
        .attr("width", 250);

    var statistics_box = statistics_content.append("rect")
        .attr("y", statistics_y + 5)
        .attr("x", -5)
        .style("fill", "white")
        .style("stroke-width", 1)
        .style("stroke", "black")
        .attr("height", 40)
        .attr("width", 250);

    statistics_content.append("text")
        .text(label)
        .attr("y", statistics_y);

    // Calculate the min and max
    var min = Math.min.apply(Math, transfusions.map(function(d){
        return d.value;
    }));
    var max = Math.max.apply(Math, transfusions.map(function(transfusion){
        return transfusion.value;
    }));

    // Calculate the median
    var sorted = transfusions.map(function(d){return parseFloat(d.value);});
    sorted = sorted.sort(sortNumber);
    s_len = sorted.length;
    if (sorted.length % 2 == 0){
        var med = (sorted[sorted.length/2-1]+sorted[sorted.length/2])/2;
    }
    else{
        var med = sorted[(sorted.length-1)/2];
    }

    statistics_content.append("text")
        .attr("y", statistics_y + 22)
        .text(function(){
            return "Quantity: " + transfusions.length;
        })
    statistics_content.append("text")
        .attr("y", statistics_y + 37)
        .text(function(){
            return "Min,Med,Max: " + min + ", " + med + ", " + max
        })

    return statistics_y + 70;
}

function sortNumber(a,b){
    return a - b;
}