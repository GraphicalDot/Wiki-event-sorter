
$(document).ready(function(){
   	App = {} ;
	window.App = App ;


function make_request(endpoint, type, data, headers){
	url =  "http://ec2-54-200-106-184.us-west-2.compute.amazonaws.com:8080/" + endpoint
//	url =  "http://localhost:5000/" + endpoint
	$.ajaxSetup({
		beforeSend: function(request){
		}});

	if (type == "GET"){
		return 	$.ajax({
			url: url,
			type: type,
	  		dataType: 'json',
	  		async: false,
			error: function(jqhr, string, errorThrown){                                                      
				var message = $.parseJSON(jqhr.responseText); 
				bootbox.alert( errorThrown +":" + jqhr.status + ",  " + "Messege:  "+ message.message);  
			},                	
		});
		}
	else {
		return 	$.ajax({
			headers: {"Content-Type": 'application/json'},
			url: url,
			type: type,
			data: data,
			statusCode: {
				404: function() {
					bootbox.alert("page not found");
					},
				401: function(){
					bootbox.alert("Error loading Page, Please try again");
				},
				400: function(){
					bootbox.alert("This has already been deactivated");
				},
			},
			dataType: 'json',
	  		async: false,
	});
		}
};

/*This is the template object which uses name as an argument to return handlebar compiled template from the the html
 */
var template = function(name){
    return Mustache.compile($("#"+name+"-template").html());
};



App.RootView = Backbone.View.extend({
	tagName: "form",
	className: "form-horizontal",
	template: template("root"),
	initialize: function(){
		console.log("Root view called")
	},
	render: function(){
		this.$el.append(this.template(this));
		console.log( this.el)
		return this;
	},
	events: {
		"click #submitQuery": "submitQuery",
	},

	submitQuery: function(event){
		event.preventDefault();
		$(".dynamic_display").empty()
		url = "search?query=" + $("#searchQuery").val()
		console.log(url)
		var jqhr = make_request(url, "GET")
		jqhr.done(function(data){
			if (data.error == false){
				var subView = new App.RootErrorRowView({model: data.data_head})
				$(".dynamic_display").append(subView.render().el);	
				$.each(data.data, function(iter, text){
					var subView = new App.RootRowView({model: text});
					$(".dynamic_display").append(subView.render().el);	
				})
				$.each(data.tags, function(iter, tag){
					$(".dynamic_display").append('<button type="button" class="btn btn-large">'+ tag +'</button>' +"&nbsp;" +"&nbsp;" +"&nbsp;");	
			
				});
				}
			else{
				bootbox.alert(data.messege)
				var subView = new App.RootErrorRowView({model: data.data})
				$(".dynamic_display").append(subView.render().el);	
			}
			})
	},
});

App.RootRowView = Backbone.View.extend({
	tagName: "form",
	className: "form-horizontal",
	template: template("root-row"),
	actualDate: function(){return this.model.actual_date},
	text: function(){return this.model.text},
	initialize: function(options){
		this.model = options.model;
	},
	render: function(){
		this.$el.append(this.template(this));
		return this;
	},
});
App.RootErrorRowView = Backbone.View.extend({
	tagName: "form",
	className: "form-horizontal",
	template: template("root-row-error"),
	text: function(){return this.model.data_tag},
	imageSrc: function(){return this.model.image_src},
	initialize: function(options){
		this.model = options.model;
	},
	render: function(){
		this.$el.append(this.template(this));
		return this;
	},
});



App.Router = Backbone.Router.extend({
	initialize: function(options){
		this.el =  options.el ;
	},

	routes: {
		"":  "welcome",
	},
	
	welcome: function(){
		console.log("Home view calledd")
		var str = new App.RootView()
		this.el.html(str.render().el);
	},
});

App.boot = function(container){
	container = $(container);
	var router = new App.Router({el: container});
	Backbone.history.start();
}
});



