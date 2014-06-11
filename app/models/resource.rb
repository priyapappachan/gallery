        #acts_as_taggable   
       # acts_as_taggable_on :tags
	
class Resource < ActiveRecord::Base
  #attr_accessible :tag_list
# searchable do
  has_many :taggings
  has_many :tags, through: :taggings
  has_attached_file :pic, :styles => { :medium => "300x300>", :thumb => "100x100>" }
  has_many :comments
  validates :pic, presence: true
  attr_accessible :tag_list,:pic,:name
# end
# for tags
  
  def self.tagged_with(name)
    Tag.find_by_name!(name).resources
  end

  def self.tag_counts
    Tag.select("tags.*, count(taggings.tag_id) as count").
      joins(:taggings).group("taggings.tag_id")
  end
  
  def tag_list
    tags.map(&:name).join(", ")
  end
  
  def tag_list=(names)
    self.tags = names.split(",").map do |n|
      Tag.where(name: n.strip).first_or_create!
    end
  end
end
