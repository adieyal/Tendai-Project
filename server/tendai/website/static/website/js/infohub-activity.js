/* The main activity feed infohub widget. */

(function() {
    if (typeof infohub == 'undefined') {
	return;
    }
    
    infohub.widget.activity = function(node) {
	this.node = node;
	this.url = 'http://infohub.org.za/widgets/activity';
	this.initialize();
	this.update();
    }
    
    infohub.widget.activity.prototype = {
	initialize: function() {
	    var style = 
		  'div.infohub>div.activity '
		+ '{ border: 1px solid #ddd; '
		+   'border-radius: 5px; '
		+   'background: #f8f8f8; } '
		+ 'div.infohub>div.activity h1 '
		+ '{ font-size: 14px; '
		+   'margin: 0px 5px; '
		+   'text-transform: uppercase; } '
		+ 'div.infohub>div.activity>div.items>div '
		+ '{ border-top: 1px solid #ddd; '
		+   'margin: 0px 5px; '
	        +   'padding: 5px 0px; } ';
	    var template = 
		  '<div class="infohub">'
		+   '<div class="activity">'
		+     '<h1>Recent activity</h1>'
		+     '<div class="items">'
		+     '</div>'
		+   '</div>'
		+ '</div>';
	    if (this.node.attr('data-style') == 'exclude') {
		this.node.html(template);
	    } else {
		this.node.html('<style>'+style+'</style>'+template);
	    }
	},
	update: function() {
	    var items = [
		{ id: 1, description: 'New medicines form submission.' },
		{ id: 2, description: 'New facility form submission.' },
		{ id: 3, description: 'New medicine stockout.' },
	    ];
	    var items = this.node
		.select('div.activity')
		.select('div.items')
		.selectAll('div')
		.data(items, function(d) { return d.id; });
	    items.enter()
		.append('div')
		.text(function(d) { return d.description; });
	    items.exit()
		.remove();
	}
    };
})();