class Tag < ActiveRecord::Base
	#attr_accessible :name
  	has_many :taggings
  	has_many :resources, through: :taggings
<<<<<<< HEAD

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

=======
end
>>>>>>> a5cf997ebe55804986943c4295f443dd635a5183
