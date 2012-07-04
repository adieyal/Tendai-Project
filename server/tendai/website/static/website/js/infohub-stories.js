/* The story feed infohub widget. */

(function() {
    if (typeof infohub == 'undefined') {
	return;
    }
    
    infohub.widget.stories = function(node) {
	this.node = node;
	var country = node.attr('data-country') || 'all';
	var count = node.attr('data-count') || 5;
	this.url = '/json/stories/?country='+country+'&count='+count;
	this.initialize();
	this.update();
    }
    
    infohub.widget.stories.prototype = {
	initialize: function() {
	    var style = '';
	    var template = 
		  '<div class="infohub">'
		+   '<div class="stories">'
		+     '<div class="items"></div>'
		+   '</div>'
		+ '</div>';
	    if (this.node.attr('data-style') == 'exclude') {
		this.node.html(template);
	    } else {
		this.node.html('<style>'+style+'</style>'+template);
	    }
	},
	update: function() {
	    var node = this.node;
	    d3.json(this.url, function(data) {
		var items = node
		    .select('div.stories')
		    .select('div.items')
		    .selectAll('div')
		    .data(data, function(d) { return d.id; });
		var story = items.enter()
		    .append('div')
	            .classed('story', true)
		    .style('background-image', function(d) { return 'url('+d.photo+')' });
		items.exit()
		    .remove();
		var d = story.append('div')
		    .classed('heading', true)
		d.append('h1')
		    .text(function(d) { return d.heading; });
		d.append('p')
		    .text(function(d) { return d.content; });
	    });
	}	    
    };
})();