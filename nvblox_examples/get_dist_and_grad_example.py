import rclpy
from nvblox_msgs.srv import GetDistAndGrad
from geometry_msgs.msg import Point
from visualization_msgs.msg import Marker, MarkerArray
from copy import deepcopy

def send_request():
    # Initialize the ROS 2 node
    rclpy.init()
    node = rclpy.create_node('my_client_node')

    # Create a client for the "add_two_ints" service
    client = node.create_client(GetDistAndGrad, '/nvblox_node/get_dist_and_grad')
    marker_publisher = node.create_publisher(MarkerArray, 'visualization_marker', 10)

    # Wait for the service to become available
    if not client.wait_for_service(timeout_sec=1.0):
        node.get_logger().info('Service not available')
        return

    # Create a request message and populate it with values
    req = GetDistAndGrad.Request()
    req.points = [
        Point(x=0.5, y=0.5, z=0.5)
    ]


    # Send the request and wait for the response
    future = client.call_async(req)
    rclpy.spin_until_future_complete(node, future)
    if future.result() is not None:
        node.get_logger().info(f'Result: {future.result().distances}')
    else:
        node.get_logger().info('Service call failed')

    # Create markers from requests
    marker_array = MarkerArray()

    # Set marker properties
    for i, (point, grad) in enumerate(zip(req.points, future.result().gradients)):
        marker_msg_ = Marker()
        marker_msg_.header.frame_id = 'map'
        marker_msg_.id = i 
        marker_msg_.type = Marker.LINE_STRIP
        marker_msg_.action = Marker.ADD
        marker_msg_.points = []
        marker_msg_.points.append(point)
        point_two = deepcopy(point)
        point_two.x += grad.x * 0.05 
        point_two.y += grad.y * 0.05 
        point_two.z += grad.z * 0.05 
        marker_msg_.points.append(point_two)
        marker_msg_.scale.x = 0.02
        marker_msg_.color.a = 1.0
        marker_msg_.color.r = 1.0
        marker_msg_.color.g = 0.0
        marker_msg_.color.b = 0.0
        
        marker_array.markers.append(marker_msg_)

    # Publish marker array
    marker_publisher.publish(marker_array)

    # Clean up the node and shutdown the ROS 2 system
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    send_request()

