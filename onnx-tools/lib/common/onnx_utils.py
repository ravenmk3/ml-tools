from typing import Optional

from google.protobuf.internal.containers import RepeatedCompositeFieldContainer
from onnx import NodeProto, ValueInfoProto


def find_node_by_input(nodes: RepeatedCompositeFieldContainer[NodeProto], input_name: str) -> Optional[NodeProto]:
    for i in range(len(nodes)):
        node = nodes[i]
        if len(node.input) == 1 and node.input[0] == input_name:
            return node
    return None


def find_node_by_output(nodes: RepeatedCompositeFieldContainer[NodeProto], output_name: str) -> Optional[NodeProto]:
    for i in range(len(nodes)):
        node = nodes[i]
        if len(node.output) == 1 and node.output[0] == output_name:
            return node
    return None


def shape_of_value_info(info: ValueInfoProto) -> list[int]:
    dims = info.type.tensor_type.shape.dim
    result = []
    for i in range(len(dims)):
        result.append(dims[i].dim_value)
    return result
