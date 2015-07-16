menu = null;  // initialise - must be global
function start_menu(args) {
  var toolbar=false, hide_root=true;
  menu = create_tree(menu_div, null, null, toolbar, hide_root);
  for (var i=0, lng=args.length; i<lng; i++) {
    var arg = args[i];
    var node_id=arg[0], parent_id=arg[1], text=arg[2], expandable=arg[3];
    menu.add_node(parent_id, node_id, expandable, text, (i===0));
    };
  menu.onselected = function(node) {
    var args = [node.node_id];
    send_request('menuitem_selected', args);
    };
  menu.onactive = function(node) {
    };
  menu.write();
  setTimeout(function() {menu.focus()}, 0);
  };
