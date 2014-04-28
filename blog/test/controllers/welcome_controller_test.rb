require 'test_helper'

class WelcomeControllerTest < ActionController::TestCase
  test "should get indez" do
    get :indez
    assert_response :success
  end

end
