from typing import Optional

from google.protobuf.internal.containers import RepeatedCompositeFieldContainer as Repeated
from onnx import NodeProto, ValueInfoProto


def find_node_by_input(nodes: Repeated[NodeProto], input_name: str) -> tuple[Optional[NodeProto], int]:
    for n in range(len(nodes)):
        node = nodes[n]
        for i in range(len(node.input)):
            if input_name == node.input[i]:
                return node, i
    return None, -1


def find_node_by_output(nodes: Repeated[NodeProto], output_name: str) -> tuple[Optional[NodeProto], int]:
    for n in range(len(nodes)):
        node = nodes[n]
        for i in range(len(node.output)):
            if output_name == node.output[i]:
                return node, i
    return None, -1


def shape_of_value_info(info: ValueInfoProto) -> list[int]:
    dims = info.type.tensor_type.shape.dim
    result = []
    for i in range(len(dims)):
        result.append(dims[i].dim_value)
    return result
