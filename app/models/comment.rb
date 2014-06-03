class Comment < ActiveRecord::Base
  belongs_to :resource
  attr_accessible :body
end
