var data;
var filters;
var selected_provider;
var titles = {'cryo': 'Cryoprecipitate', 'plasma': 'Plasma', 'platelets': 'Platelets', 'rbcs': 'Red Blood Cells'};

$(document).ready(function(){
    var criteria = {"products": 'ALL', "location":'', "specialty":'', "per_day":'',
                    "start_date":'', "end_date":''};
    $.getJSON("/utilization/utilization_data/", criteria, function(utilization_data) {
        data = utilization_data;
        filters = get_filters();
        create_provider_graph(data, filters);
    });

    d3.select('#providers-svg').on('click', function(){
        var target = d3.event.target;
        var target_class = d3.select(target).attr('class') || '';
        if (target_class.includes('box') || target_class.includes('median')){
            var selected_specialty = d3.select(target).attr('data-specialty');
            selected_provider = d3.select(target).attr('data-provider');
            filters.specialty = selected_specialty;
            create_provider_graph(data, filters);
            $('#title-div').html(titles[filters.product]+' - ' +selected_specialty)
        } else {
            filters = get_filters();
            selected_provider = '';
            create_provider_graph(data, filters);
        }
    })
});

$(document).on('click', '#draw-button', function(){
    filters = get_filters();
    create_provider_graph(data, filters);
});

function create_provider_graph(data, filters){
    // Figure out what test to look at based on what product is selected
    var product_to_test = {'cryo': 'fibrinogen_', 'plasma': 'prothrombin_', 'platelets': 'platelet_',
                           'rbcs': 'hemoglobin_'};
    var lab = product_to_test[filters.product];

    var product_names = {'cryo': 'CRYOPPT', 'plasma': 'PLASMA', 'platelets': 'PLATELETS', 'rbcs': 'RED CELLS'};
    var product_name = product_names[filters.product];

    $('#title-div').html(titles[filters.product]+' - All Providers')
    var svg = d3.select('#providers-svg');
    svg.selectAll('g').remove();

    var filtered_providers = data.providers;
    if (filters.num_units != ''){
        filtered_providers = filtered_providers.filter(x => x['num_'+filters.product] >= filters.num_units);
    } else {
        filtered_providers = filtered_providers.filter(x => x['num_'+filters.product] > 0);
    }
    if (filters.specialty != undefined){
        filtered_providers = filtered_providers.filter(x => x.specialty == filters.specialty);
    }

    // Sort the providers by highest median test value
    filtered_providers.sort(function(a, b){ return b[lab+'med'] - a[lab+'med'] });
    console.log(filtered_providers)

    var provider_names = filtered_providers.map(x => x.name);

    var div_width = $('#providers-container').width();
    if (filtered_providers.length * 30 < div_width){var width = div_width}
    else {var width = filtered_providers.length * 30}
    var height = 560;
    svg.attr('width', width);
    svg.attr('height', height);

    var x = d3.scaleBand()
        .domain(provider_names)
        .range([50, width]);

    var xAxis = d3.axisBottom()
        .scale(x);

    var test_values = filtered_providers.map(x => x[lab+'max']);
    var max = d3.max(test_values);
    var y = d3.scaleLinear()
        .domain([-2, max])
        .range([410, 20]);

    var yAxis = d3.axisLeft()
        .scale(y)
        .tickFormat(function(d){
            if (d != -2){ return d}
            else { return "None" }
         });

    svg.append('g')
        .attr('transform', 'translate(50, 0)')
        .call(yAxis);

    svg.append('g')
        .attr('transform', 'translate(0, 410)')
        .call(xAxis)
        .selectAll('text')
            .attr('transform', 'rotate(-50)')
            .attr('text-anchor', 'end');

    if (provider_names.length>1){
        var tick_spacing = x(provider_names[1]) - x(provider_names[0]);
    } else {
        var tick_spacing = width;
    }
    var data_g = svg.append('g');
    var overall_median = data_g.append('line')
        .attr('x1', 50).attr('x2', width)
        .attr('y1', y(data[product_name].median)).attr('y2', y(data[product_name].median))
        .attr('stroke', 'rgba(0, 0, 0, 0.2)').attr('stroke-width', 3).attr('stroke-dasharray', '4 4');

    var lines = data_g.selectAll('.prov-line')
        .data(filtered_providers)
        .enter()
        .append('line')
            .attr('class', 'prov-line')
            .attr('x1', function(d){ return x(d.name) + tick_spacing/2 })
            .attr('x2', function(d){ return x(d.name) + tick_spacing/2 })
            .attr('y1', 10)
            .attr('y2', 410)
            .attr('stroke', 'rgba(0, 0, 0, .05)')
            .attr('stroke-width', '1');

    var numbers = data_g.selectAll('.number')
        .data(filtered_providers)
        .enter()
        .append('text')
            .text(function(d){ return d['num_'+filters.product] }).attr('text-anchor', 'middle').attr('font-size', '11')
            .attr('class', 'number')
            .attr('x', function(d){ return x(d.name) + tick_spacing/2 })
            .attr('y', function(d){return y(d[lab+'max'])-4});

    var boxes = data_g.selectAll('.box')
        .data(filtered_providers)
        .enter()
        .append('rect')
            .attr('class', 'box')
            .attr('stroke', 'black')
            .attr('stroke-width', '2')
            .attr('fill', function(d){
                if (d.name==selected_provider){return 'var(--red)'}
                else { return '#97C7EF'}
            })
            .attr('x', function(d){ return x(d.name) + tick_spacing/2 - 3 })
            .attr('y', function(d){ return y(d[lab+'max']) })
            .attr('height', function(d){
                return y(d[lab+'min']) - y(d[lab+'max']);
            })
            .attr('width', 6)
            .attr('data-specialty', function(d){ return d.specialty })
            .attr('data-provider', function(d){ return d.name });

    var medians = data_g.selectAll('.median')
        .data(filtered_providers)
        .enter()
        .append('circle')
            .attr('class', 'median')
            .attr('r', '3')
            .attr('cx', function(d){ return x(d.name) + tick_spacing/2 })
            .attr('cy', function(d){return y(d[lab+'med'])})
            .attr('data-specialty', function(d){ return d.specialty });;

}

function get_filters(){
    var filters = new Object();
    filters.product = $('#examine-select').val();
    filters.num_units = $('#num-units-input').val();
    return filters;
}
