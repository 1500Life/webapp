window.onload = function () {
    var chart = new CanvasJS.Chart("followers",
    {
      exportEnabled: true,
      animationEnabled: true,
      title:{
        text: "User Follow Chart"
    },
    axisX:{
        title: "time",
        gridThickness: 2
    },
    axisY: {
        title: "Follow"
    },
    data: [
    {        
        type: "column",
        name: "Followers",
        showInLegend: true,
        dataPoints: [
        {% for user in users %}
        { x: new Date('{{ user.timestap|date:"Y-m-d H:i" }}'), y: {{ user.followers_count }} },
        {% endfor %}
        ]
    },
    {        
        type: "column",
        name: "Following",
        showInLegend: true,
        dataPoints: [
        {% for user in users %}
        { x: new Date('{{ user.timestap|date:"Y-m-d H:i" }}'), y: {{ user.friends_count }} },
        {% endfor %}
        ]
    },
    ]
});
chart.render();

var tweet = new CanvasJS.Chart("tweets",
    {
        exportEnabled: true,
        animationEnabled: true,
        title:{
        text: "User Tweet Chart"
    },
    axisX:{
        title: "time",
        gridThickness: 2
    },
    axisY: {
        title: "Tweet"
    },
    data: [
    {        
        type: "line",
        name: "Tweet",
        showInLegend: true,
        dataPoints: [
        {% for user in users %}
        { x: new Date('{{ user.timestap|date:"Y-m-d H:i" }}'), y: {{ user.statuses_count }} },
        {% endfor %}
        ]
    },
    {        
        type: "line",
        name: "Favorites",
        showInLegend: true,
        dataPoints: [
        {% for user in users %}
        { x: new Date('{{ user.timestap|date:"Y-m-d H:i" }}'), y: {{ user.favourites_count }} },
        {% endfor %}
        ]
    },
    ]
});
tweet.render();

}