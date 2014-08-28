menu = null;  // initialise
function start_menu(args) {
  var menu_obj = {};  //new Object();

  //debug3(JSON.stringify(args));

  for (var i=0, l=args.length; i<l; i++) {
    var arg = args[i];
    var parent_id = arg[0];
    var text = arg[1];
    var expandable = arg[2];
    var node_id = arg[3];
    if (parent_id == 0) {
      menu = create_tree(menu_div);
      menu_obj[node_id] = menu;
      }
    else {
      var parent = menu_obj[parent_id];
      var node = add_node(parent, node_id, expandable, text);
      menu_obj[node_id] = node;
      node.onselected = function() {
        var args = [this.node_id];
        send_request('menuitem_selected', args);
        };
      };
    };
  menu.write();
  setTimeout(function() {menu.focus()}, 0);
  };
