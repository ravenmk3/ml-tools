import onnx
from onnx import TensorProto

from lib.common.file import read_valid_lines
from lib.common.onnx_utils import find_node_by_output


def clf_add_post_process(model_path: str, output_file: str,
                         name_file: str = None, num_output: int = 5,
                         multilabel: bool = False, check: bool = True):
    print('load model:', model_path)
    model = onnx.load(model_path)
    graph = model.graph
    nodes = graph.node
    outputs = graph.output
    assert len(outputs) == 1

    head_output_name = 'head_output'
    prob_output_name = 'prob_output'

    o_output = outputs.pop()
    o_output_node, o_output_idx = find_node_by_output(nodes, o_output.name)
    o_output_node.output[o_output_idx] = head_output_name

    gather_index_node = onnx.helper.make_node(
        'Constant', inputs=[], outputs=['gather_index'], name='gather_index',
        value=onnx.helper.make_tensor('gather_index', TensorProto.INT64, dims=(), vals=[0])
    )
    gather_node = onnx.helper.make_node(
        'Gather', inputs=[head_output_name, 'gather_index'], outputs=['gather_output'], name='gather', axis=0)
    nodes.extend([gather_index_node, gather_node])

    if multilabel:
        act_fn_node = onnx.helper.make_node(
            'Sigmoid', inputs=['gather_output'], outputs=[prob_output_name])
    else:
        act_fn_node = onnx.helper.make_node(
            'Softmax', inputs=['gather_output'], outputs=[prob_output_name])
    nodes.append(act_fn_node)

    const_topk_k = onnx.helper.make_tensor('k', TensorProto.INT64, dims=(1,), vals=[num_output])
    graph.initializer.append(const_topk_k)

    topk_node = onnx.helper.make_node(
        'TopK', inputs=[prob_output_name, 'k'], outputs=['scores', 'indices'], axis=-1, largest=1, sorted=1)
    nodes.append(topk_node)

    scores_output = onnx.helper.make_tensor_value_info('scores', TensorProto.FLOAT, (num_output,))
    indices_output = onnx.helper.make_tensor_value_info('indices', TensorProto.INT64, (num_output,))
    outputs.extend([scores_output, indices_output])

    if name_file:
        names = read_valid_lines(name_file)
        names = [x.encode('utf-8') for x in names]
        names_node = onnx.helper.make_node(
            'Constant',
            inputs=[],
            outputs=['all_names'],
            value=onnx.helper.make_tensor(
                name='all_names',
                data_type=onnx.TensorProto.STRING,
                dims=[len(names)],
                vals=names,
            ),
        )
        gather_elms_node = onnx.helper.make_node(
            'GatherElements',
            inputs=['all_names', 'indices'],
            outputs=['names'],
            axis=0,
        )
        nodes.extend([names_node, gather_elms_node])
        names_output = onnx.helper.make_tensor_value_info('names', TensorProto.STRING, (num_output,))
        outputs.append(names_output)

    if check:
        print('check model')
        onnx.checker.check_model(model, full_check=True)

    print('save to:', output_file)
    onnx.save(model, output_file)
    print('all done')
