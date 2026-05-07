import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped

class RobotMover(Node):
    def __init__(self):
        super().__init__('robot_mover')
        self.publisher = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.move)
        self.get_logger().info('RobotMover node started')

    def move(self):
        msg = TwistStamped()
        msg.twist.linear.x = 0.2
        msg.twist.angular.z = 0.5
        self.publisher.publish(msg)

    def stop(self):
        msg = TwistStamped()
        msg.twist.linear.x = 0.0
        msg.twist.angular.z = 0.0
        self.publisher.publish(msg)
        self.get_logger().info('Robot stopped')

def main():
    rclpy.init()
    node = RobotMover()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.stop()
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()