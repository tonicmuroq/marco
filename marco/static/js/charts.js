function drawLineChart(data, type, xLabel, yLabel, format) {
  nv.addGraph(function() {
    var chart = nv.models.lineChart().height(400).width(800);
    chart.xAxis.axisLabel(xLabel)
      .tickFormat(function(d) {
        return d3.time.format('%X')(new Date(d));
    });
    chart.yAxis.axisLabel(yLabel).tickFormat(d3.format(format));
  
    d3.select('#'+type)
        .datum(data)
        .transition()
        .attr('height', 400)
        .attr('width', 800)
        .call(chart);
  
    nv.utils.windowResize(chart.update);
  
    return chart;
  });
}

function metricChart(name, xLabel, yLabel, format, timeout) {
  var s = $('#'+name),
    url = s.data('url');
  $.get(url, function(d) {
    drawLineChart(d.data, name, xLabel, yLabel, format);
  });
  setInterval(function() {
    $.get(url, function(d) {
      drawLineChart(d.data, name, xLabel, yLabel, format);
    });
  }, timeout);
}
