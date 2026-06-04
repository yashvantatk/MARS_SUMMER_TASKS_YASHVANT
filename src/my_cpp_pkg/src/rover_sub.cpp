#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
using std::placeholders::_1;

class RoverSubscriber : public rclcpp::Node
{
public:
  RoverSubscriber() : Node("rover_subscriber")
  {
    subscription_ = this->create_subscription<std_msgs::msg::String>(
      "ares_nova_telemetry", 10, std::bind(&RoverSubscriber::topic_callback, this, _1));
  }

private:
  void topic_callback(const std_msgs::msg::String & msg) const
  {
    RCLCPP_INFO(this->get_logger(), "Received Data: '%s'", msg.data.c_str());
  }
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<RoverSubscriber>());
  rclcpp::shutdown();
  return 0;
}
