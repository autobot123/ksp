>>> # get a node object
>>> node = vessel.control.nodes[0]
>>> for attributes in dir(node):
	 print(attributes, (getattr(node, attributes)))


__class__ <class 'krpc.types.Node'>
__delattr__ <method-wrapper '__delattr__' of Node object at 0x04B3B970>
__dict__ {'_object_id': 34}
__dir__ <built-in method __dir__ of Node object at 0x04B3B970>
__doc__ Represents a maneuver node. Can be created using SpaceCenter.Control.add_node.
__eq__ <bound method ClassBase.__eq__ of <SpaceCenter.Node remote object #34>>
__format__ <built-in method __format__ of Node object at 0x04B3B970>
__ge__ <bound method ClassBase.__ge__ of <SpaceCenter.Node remote object #34>>
__getattribute__ <method-wrapper '__getattribute__' of Node object at 0x04B3B970>
__gt__ <bound method ClassBase.__gt__ of <SpaceCenter.Node remote object #34>>
__hash__ <bound method ClassBase.__hash__ of <SpaceCenter.Node remote object #34>>
__init__ <bound method ClassBase.__init__ of <SpaceCenter.Node remote object #34>>
__init_subclass__ <built-in method __init_subclass__ of type object at 0x049713E0>
__le__ <bound method ClassBase.__le__ of <SpaceCenter.Node remote object #34>>
__lt__ <bound method ClassBase.__lt__ of <SpaceCenter.Node remote object #34>>
__module__ krpc.types
__ne__ <bound method ClassBase.__ne__ of <SpaceCenter.Node remote object #34>>
__new__ <built-in method __new__ of type object at 0x6D258140>
__reduce__ <built-in method __reduce__ of Node object at 0x04B3B970>
__reduce_ex__ <built-in method __reduce_ex__ of Node object at 0x04B3B970>
__repr__ <bound method ClassBase.__repr__ of <SpaceCenter.Node remote object #34>>
__setattr__ <method-wrapper '__setattr__' of Node object at 0x04B3B970>
__sizeof__ <built-in method __sizeof__ of Node object at 0x04B3B970>
__str__ <method-wrapper '__str__' of Node object at 0x04B3B970>
__subclasshook__ <built-in method __subclasshook__ of type object at 0x049713E0>
__weakref__ None
_add_method <bound method DynamicType._add_method of <class 'krpc.types.Node'>>
_add_property <bound method DynamicType._add_property of <class 'krpc.types.Node'>>
_add_static_method <bound method DynamicType._add_static_method of <class 'krpc.types.Node'>>
_class_name Node
_client None
_object_id 34
_service_name SpaceCenter
burn_vector <bound method <lambda> of <SpaceCenter.Node remote object #34>>
delta_v 68.80347769664972
direction <bound method <lambda> of <SpaceCenter.Node remote object #34>>
normal 0.0
orbit <SpaceCenter.Orbit remote object #35>
orbital_reference_frame <SpaceCenter.ReferenceFrame remote object #36>
position <bound method <lambda> of <SpaceCenter.Node remote object #34>>
prograde 0.0
radial -68.80347769664972
reference_frame <SpaceCenter.ReferenceFrame remote object #37>
remaining_burn_vector <bound method <lambda> of <SpaceCenter.Node remote object #34>>
remaining_delta_v 68.80161030201279
remove <bound method <lambda> of <SpaceCenter.Node remote object #34>>
time_to 583.6903757205073
ut 63061.949037886065