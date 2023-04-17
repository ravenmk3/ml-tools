import onnx
from onnx import TensorProto

from lib.common.onnx_utils import shape_of_value_info, find_node_by_input


def clf_add_pre_process(model_path: str, output_file: str, check: bool = True):
    """
    添加图像预处理操作到 ONNX 模型，包括
    1. Transpose (H x W x C) -> (C x H x W)
    2. Normalize(mean, std)，由于前面省略掉了除以 255 将值变为 [0-1] 的操作，所以 mean 和 std 的值都各乘以 255 以计算出一致的结果

    :param model_path: 输入模型文件的路径
    :param output_file: 输出模型文件的路径
    :param check: 是否检查模型有效性
    """

    print('load model:', model_path)
    model = onnx.load(model_path)
    graph = model.graph
    nodes = graph.node
    inputs = graph.input

    o_input = inputs.pop()
    o_input_shape = shape_of_value_info(o_input)
    o_input_node, o_input_idx = find_node_by_input(nodes, o_input.name)

    input_name = 'input'
    input_shape = tuple(o_input_shape[1:])
    input_shape = (input_shape[1], input_shape[2], input_shape[0])
    input_info = onnx.helper.make_tensor_value_info(input_name, TensorProto.UINT8, input_shape)
    inputs.append(input_info)
    node_idx = 0

    transpose_node = onnx.helper.make_node(
        'Transpose',
        inputs=[input_name],
        outputs=['transposed'],
        perm=(2, 0, 1),
    )
    nodes.insert(node_idx, transpose_node)
    node_idx += 1

    cast_node = onnx.helper.make_node(
        'Cast',
        inputs=['transposed'],
        outputs=['cast_output'],
        to=TensorProto.FLOAT,
    )
    nodes.insert(node_idx, cast_node)
    node_idx += 1

    normalize_mean = onnx.helper.make_node(
        'Constant', inputs=[], outputs=['normalize_mean'],
        value=onnx.helper.make_tensor(
            'normalize_mean', TensorProto.FLOAT, dims=(3, 1, 1), vals=[123.675, 116.28, 103.53])
    )

    normalize_std = onnx.helper.make_node(
        'Constant', inputs=[], outputs=['normalize_std'],
        value=onnx.helper.make_tensor(
            'normalize_std', TensorProto.FLOAT, dims=(3, 1, 1), vals=[58.395, 57.12, 57.375])
    )

    nodes.insert(node_idx, normalize_mean)
    node_idx += 1

    nodes.insert(node_idx, normalize_std)
    node_idx += 1

    normalize_sub = onnx.helper.make_node(
        'Sub',
        inputs=['cast_output', 'normalize_mean'],
        outputs=['normalize_mean_output'],
    )

    normalize_div = onnx.helper.make_node(
        'Div',
        inputs=['normalize_mean_output', 'normalize_std'],
        outputs=['normalize_output'],
    )

    nodes.insert(node_idx, normalize_sub)
    node_idx += 1

    nodes.insert(node_idx, normalize_div)
    node_idx += 1

    unsqueeze_axes = onnx.helper.make_tensor('unsqueeze_axes', TensorProto.INT64, dims=(1,), vals=[0])
    graph.initializer.append(unsqueeze_axes)

    unsqueeze_node = onnx.helper.make_node(
        'Unsqueeze',
        inputs=['normalize_output', 'unsqueeze_axes'],
        outputs=['unsqueeze_output'],
    )
    nodes.insert(node_idx, unsqueeze_node)

    o_input_node.input[o_input_idx] = 'unsqueeze_output'

    if check:
        print('check model')
        onnx.checker.check_model(model, full_check=True)

    print('save to:', output_file)
    onnx.save(model, output_file)
    print('all done')
